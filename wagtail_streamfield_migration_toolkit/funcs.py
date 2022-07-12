from django.db.models import JSONField, F
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

    # TODO for revisions
