from django.db.models import JSONField, F
from django.db.models.functions import Cast
from wagtail.blocks import StreamValue

from wagtail_streamfield_migration_toolkit import utils


def stream_data_migration(
    apps,
    schema_editor,
    app_name,
    model_name,
    field_name,
    block_path_str,
    operation,
    with_revisions=False,
):
    page_model = apps.get_model(app_name, model_name)

    for page in page_model.objects.annotate(
        raw_content=Cast(F(field_name), JSONField())
    ).all():

        altered_raw_data = utils.apply_changes_to_raw_data(
            raw_data=page.raw_content,
            block_path_str=block_path_str,
            operation=operation,
            streamfield=getattr(page_model, field_name),
        )

        stream_block = getattr(page, field_name).stream_block
        setattr(
            page, field_name, StreamValue(stream_block, altered_raw_data, is_lazy=True)
        )

        page.save()

    # iterate over pages
    # - rename_blocks_in_raw_content for each page
    # - TODO add a return value to util to know if changes were made
    # - TODO save changed only
    # -
    # TODO for revisions
