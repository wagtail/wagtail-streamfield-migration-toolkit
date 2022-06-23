from wagtail_streamfield_migration_toolkit import utils


def rename_data_migration(
    apps,
    schema_editor,
    app_name,
    model_name,
    field_name,
    block_path,
    new_name,
    with_revisions=False,
):
    page_model = apps.get_model(app_name, model_name)
    # TODO get raw data
    # TODO parse block path
    # TODO iterate over pages
    # - TODO rename_blocks_in_raw_data for each page
    pass
