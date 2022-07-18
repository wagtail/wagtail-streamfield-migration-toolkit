import json
from django.db.models import JSONField, F, Subquery, OuterRef
from django.db.models.functions import Cast
from wagtail.blocks import StreamValue

from wagtail_streamfield_migration_toolkit import utils


def migrate_stream_data(
    apps,
    schema_editor,
    app_name,
    model_name,
    field_name,
    block_path_str,
    operation,
    with_revisions=False,
    revision_limit=None,
    chunk_size=1024,
):
    page_model = apps.get_model(app_name, model_name)

    page_queryset = page_model.objects.annotate(
        raw_content=Cast(F(field_name), JSONField())
    ).all()
    updated_pages_buffer = []
    for page in page_queryset.iterator(chunk_size=chunk_size):

        altered_raw_data = utils.apply_changes_to_raw_data(
            raw_data=page.raw_content,
            block_path_str=block_path_str,
            operation=operation,
            streamfield=getattr(page_model, field_name),
        )
        # - TODO add a return value to util to know if changes were made - Where would this be added?
        # - TODO save changed only

        stream_block = getattr(page, field_name).stream_block
        setattr(
            page, field_name, StreamValue(stream_block, altered_raw_data, is_lazy=True)
        )
        updated_pages_buffer.append(page)

        if len(updated_pages_buffer) == chunk_size:
            page_model.objects.bulk_update(updated_pages_buffer, [field_name])
            updated_pages_buffer = []

    if len(updated_pages_buffer) > 0:
        page_model.objects.bulk_update(updated_pages_buffer, [field_name])

    if with_revisions:
        ContentType = apps.get_model("contenttypes", "ContentType")
        PageRevision = apps.get_model("wagtailcore", "PageRevision")
        contenttype_id = ContentType.objects.get_for_model(page_model).id

        if revision_limit is not None:
            revision_queryset = PageRevision.objects.filter(
                id__in=Subquery(
                    PageRevision.objects.filter(page_id=OuterRef("page_id"))
                    .order_by("-created_at")
                    .values_list("id", flat=True)[:revision_limit]
                ),
                page__content_type_id=contenttype_id,
            )
        else:
            revision_queryset = PageRevision.objects.filter(
                page__content_type_id=contenttype_id,
            )

        updated_revisions_buffer = []
        for revision in revision_queryset.iterator(chunk_size=chunk_size):

            altered_raw_data = utils.apply_changes_to_raw_data(
                raw_data=json.loads(revision.content[field_name]),
                block_path_str=block_path_str,
                operation=operation,
                streamfield=getattr(page_model, field_name),
            )
            # - TODO add a return value to util to know if changes were made - Where would this be added?
            # - TODO save changed only

            revision.content[field_name] = json.dumps(altered_raw_data)
            updated_revisions_buffer.append(revision)

            if len(updated_revisions_buffer) == chunk_size:
                PageRevision.objects.bulk_update(updated_revisions_buffer, ["content"])
                updated_revisions_buffer = []

        if len(updated_revisions_buffer) > 0:
            PageRevision.objects.bulk_update(updated_revisions_buffer, ["content"])
