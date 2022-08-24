import json
import logging
from django.db.models import JSONField, F, Q, Subquery, OuterRef
from django.db.models.functions import Cast
from django.db.migrations import RunPython
from wagtail.blocks import StreamValue
from wagtail import VERSION as WAGTAIL_VERSION

from wagtail_streamfield_migration_toolkit import utils

logger = logging.getLogger(__name__)


class MigrateStreamData(RunPython):
    """Subclass of RunPython for streamfield data migration operations"""

    def __init__(
        self,
        app_name,
        model_name,
        field_name,
        operations_and_block_paths,
        revisions_from=None,
        chunk_size=1024,
        **kwargs
    ):
        """MigrateStreamData constructor

        Args:
            app_name (str): Name of the app.
            model_name (str): Name of the model.
            field_name (str): Name of the streamfield.
            operations_and_block_paths (:obj:`list` of :obj:`tuple` of (:obj:`operation`, :obj:`str`)):
                List of operations and corresponding block paths to apply.
            revisions_from (:obj:`datetime`, optional): Only revisions created from this date
                onwards will be updated. Passing `None` updates all revisions. Defaults to `None`.
                Note that live and latest revisions will be updated regardless of what value this
                takes.
            chunk_size (:obj:`int`, optional): chunk size for queryset.iterator and bulk_update.
                Defaults to 1024.
            **kwargs: atomic, elidable, hints for superclass RunPython can be given

        Example:
            Renaming a block named `field1` to `block1`::
                MigrateStreamData(
                    app_name="blog",
                    model_name="BlogPage",
                    field_name="content",
                    operations_and_block_paths=[
                        (RenameStreamChildrenOperation(old_name="field1", new_name="block1"), ""),
                    ],
                    revisions_from=datetime.date(2022, 7, 25)
                ),
        """

        self.app_name = app_name
        self.model_name = model_name
        self.field_name = field_name
        self.operations_and_block_paths = operations_and_block_paths
        self.revisions_from = revisions_from
        self.chunk_size = chunk_size

        # TODO add reverse code when needed, will probably need another input (reversible?)
        # super class kwargs - atomic,elidable,hints
        super().__init__(
            code=self.migrate_stream_data_forward,
            reverse_code=lambda *args: None,
            **kwargs
        )

    def migrate_stream_data_forward(self, apps, schema_editor):
        model = apps.get_model(self.app_name, self.model_name)

        self.prepare_revision_query_helper_values(apps, model)

        model_queryset = model.objects.annotate(
            raw_content=Cast(F(self.field_name), JSONField())
        ).all()

        updated_model_instances_buffer = []
        for instance in model_queryset.iterator(chunk_size=self.chunk_size):

            self.prepare_live_and_latest_revision_ids_from_instance(instance)

            raw_data = instance.raw_content
            for operation, block_path_str in self.operations_and_block_paths:
                try:
                    raw_data = utils.apply_changes_to_raw_data(
                        raw_data=raw_data,
                        block_path_str=block_path_str,
                        operation=operation,
                        streamfield=getattr(model, self.field_name),
                    )
                    # - TODO add a return value to util to know if changes were made
                    # - TODO save changed only
                except utils.InvalidBlockDefError as e:
                    raise utils.InvalidBlockDefError(instance=instance) from e

            stream_block = getattr(instance, self.field_name).stream_block
            setattr(
                instance,
                self.field_name,
                StreamValue(stream_block, raw_data, is_lazy=True),
            )
            updated_model_instances_buffer.append(instance)

            if len(updated_model_instances_buffer) == self.chunk_size:
                model.objects.bulk_update(
                    updated_model_instances_buffer, [self.field_name]
                )
                updated_model_instances_buffer = []

        if len(updated_model_instances_buffer) > 0:
            # For any remaining chunks
            model.objects.bulk_update(updated_model_instances_buffer, [self.field_name])

        # For models without revisions
        if not self.has_revisions:
            return

        revision_queryset = self.RevisionModel.objects.filter(self.revision_query)

        updated_revisions_buffer = []
        for revision in revision_queryset.iterator(chunk_size=self.chunk_size):

            raw_data = json.loads(revision.content[self.field_name])
            for operation, block_path_str in self.operations_and_block_paths:
                try:
                    raw_data = utils.apply_changes_to_raw_data(
                        raw_data=raw_data,
                        block_path_str=block_path_str,
                        operation=operation,
                        streamfield=getattr(model, self.field_name),
                    )
                except utils.InvalidBlockDefError as e:
                    # TODO this check might be a problem with wagtail 3.0
                    if revision.id not in live_and_latest_revision_ids:
                        logger.exception(
                            utils.InvalidBlockDefError(
                                revision=revision, instance=instance
                            )
                        )
                        continue
                    else:
                        raise utils.InvalidBlockDefError(
                            revision=revision, instance=instance
                        ) from e
                # - TODO add a return value to util to know if changes were made
                # - TODO save changed only

            revision.content[self.field_name] = json.dumps(raw_data)
            updated_revisions_buffer.append(revision)

            if len(updated_revisions_buffer) == self.chunk_size:
                self.RevisionModel.objects.bulk_update(
                    updated_revisions_buffer, ["content"]
                )
                updated_revisions_buffer = []

        if len(updated_revisions_buffer) > 0:
            self.RevisionModel.objects.bulk_update(
                updated_revisions_buffer, ["content"]
            )

    def prepare_revision_query_helper_values(self, apps, model):
        """Prepare variables which are needed for building up the revision query.

        Note: Since the PageRevision model has been replaced with the Revision model from wagtail 4
            onwards, we need somewhat different logic for wagtail 3 and for 4+.
        """

        if WAGTAIL_VERSION < (4, 0, 0):
            # only pages have revisions
            if issubclass(model, apps.get_model("wagtailcore", "Page")):
                self.has_revisions = True
                self.has_live_revisions = True
                self.RevisionModel = apps.get_model("wagtailcore", "PageRevision")
                self.page_ids = []
                self.live_revision_ids = set()

                # if revisions_from is given, then query only the revisions created after that
                # datetime (and the latest and live revisions if they are not after revisions_from)
                if self.revisions_from is not None:
                    # All revisions created after the given date.
                    revision_query = Q(
                        created_at__gte=self.revisions_from,
                        page_id__in=self.page_ids,
                    )
                    # All live revisions.
                    revision_query = revision_query | Q(id__in=self.live_revision_ids)
                    # All latest revisions. For each revision, we check if it is the revision with the
                    # last `created_at` from all revisions with its `page_id`.
                    revision_query = revision_query | Q(
                        id__in=Subquery(
                            self.RevisionModel.objects.filter(
                                page_id=OuterRef("page_id")
                            )
                            .order_by("-created_at", "-id")
                            .values_list("id", flat=True)[:1]
                        ),
                        page_id__in=self.page_ids,
                    )
                    self.revision_query = revision_query

                # otherwise query all revisions for the page
                else:
                    self.revision_query = Q(page_id__in=self.page_ids)

            else:
                self.has_revisions = False
                self.has_live_revisions = False

        else:
            self.RevisionModel = apps.get_model("wagtailcore", "Revision")

            # We check if the models have a field `latest_revision` and make sure it points to the
            # Revision model. This relation is there on models with `RevisionMixin`.
            self.has_latest_revisions = (
                hasattr(model, "latest_revision")
                and model.latest_revision.field.remote_field.model is self.RevisionModel
            )
            # Again, check for `live_revision`
            self.has_live_revisions = (
                hasattr(model, "live_revision")
                and model.live_revision.field.remote_field.model is self.RevisionModel
            )
            self.has_revisions = self.has_latest_revisions or self.has_live_revisions

            if self.has_revisions:
                # use a set here since latest_revisions and live_revisions can overlap often
                self.live_and_latest_revision_ids = set()

                ContentType = apps.get_model("contenttypes", "ContentType")
                contenttype_id = ContentType.objects.get_for_model(model).id

                # if revisions_from is given, then query only the revisions created after that
                # datetime (and the latest and live revisions if they are not after revisions_from)
                if self.revisions_from is not None:
                    # All revisions created after the given date.
                    revision_query = Q(
                        created_at__gte=self.revisions_from,
                        content_type_id=contenttype_id,
                    )
                    # All live and latest revisions
                    revision_query = revision_query | Q(
                        id__in=self.live_and_latest_revision_ids
                    )
                    self.revision_query = revision_query

                # otherwise query all revisions for the model
                else:
                    self.revision_query = Q(content_type_id=contenttype_id)

    def prepare_live_and_latest_revision_ids_from_instance(self, instance):

        if WAGTAIL_VERSION < (4, 0, 0) and self.has_revisions:
            self.page_ids.append(instance.id)
            self.live_revision_ids.add(instance.live_revision_id)

        elif self.has_revisions:
            # From wagtail 4 onwards, there can be non page models which may have live or latest
            # revisions, but not necessarily having both at the same time.
            if self.has_latest_revisions:
                self.live_and_latest_revision_ids.add(instance.latest_revision_id)

            if self.has_live_revisions:
                self.live_and_latest_revision_ids.add(instance.live_revision_id)
