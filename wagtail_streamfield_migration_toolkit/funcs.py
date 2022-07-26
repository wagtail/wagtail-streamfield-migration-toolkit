import json
from django.db.models import JSONField, F
from django.db.models.functions import Cast
from django.db.migrations import RunPython
from wagtail.blocks import StreamValue

from wagtail_streamfield_migration_toolkit import utils


class MigrateStreamData(RunPython):
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
        # TODO add checks to validate
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
        page_model = apps.get_model(self.app_name, self.model_name)

        page_queryset = page_model.objects.annotate(
            raw_content=Cast(F(self.field_name), JSONField())
        ).all()
        updated_pages_buffer = []
        for page in page_queryset.iterator(chunk_size=self.chunk_size):

            altered_raw_data = page.raw_content
            for operation, block_path_str in self.operations_and_block_paths:
                altered_raw_data = utils.apply_changes_to_raw_data(
                    raw_data=altered_raw_data,
                    block_path_str=block_path_str,
                    operation=operation,
                    streamfield=getattr(page, self.field_name),
                )
                # - TODO add a return value to util to know if changes were made - Where would this be added?
                # - TODO save changed only

            stream_block = getattr(page, self.field_name).stream_block
            setattr(
                page,
                self.field_name,
                StreamValue(stream_block, altered_raw_data, is_lazy=True),
            )
            updated_pages_buffer.append(page)

            if len(updated_pages_buffer) == self.chunk_size:
                page_model.objects.bulk_update(
                    updated_pages_buffer, [self.field_name]
                )
                updated_pages_buffer = []

        if len(updated_pages_buffer) > 0:
            # For any remaining chunks
            page_model.objects.bulk_update(updated_pages_buffer, [self.field_name])

        ContentType = apps.get_model("contenttypes", "ContentType")
        PageRevision = apps.get_model("wagtailcore", "PageRevision")
        contenttype_id = ContentType.objects.get_for_model(page_model).id

        if self.revisions_from is not None:
            revision_queryset = PageRevision.objects.filter(
                created_at__gte=self.revisions_from, content_type_id=contenttype_id
            )
        else:
            revision_queryset = PageRevision.objects.filter(
                content_type_id=contenttype_id,
            )

        updated_revisions_buffer = []
        for revision in revision_queryset.iterator(chunk_size=self.chunk_size):

            altered_raw_data = json.loads(revision.content[self.field_name])
            for operation, block_path_str in self.operations_and_block_paths:
                altered_raw_data = utils.apply_changes_to_raw_data(
                    raw_data=altered_raw_data,
                    block_path_str=block_path_str,
                    operation=operation,
                    streamfield=getattr(page, self.field_name),
                )
                # - TODO add a return value to util to know if changes were made - Where would this be added?
                # - TODO save changed only

            revision.content[self.field_name] = json.dumps(altered_raw_data)
            updated_revisions_buffer.append(revision)

            if len(updated_revisions_buffer) == self.chunk_size:
                PageRevision.objects.bulk_update(updated_revisions_buffer, ["content"])
                updated_revisions_buffer = []

        if len(updated_revisions_buffer) > 0:
            PageRevision.objects.bulk_update(updated_revisions_buffer, ["content"])
