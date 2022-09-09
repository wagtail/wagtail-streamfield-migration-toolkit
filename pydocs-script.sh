pydoc-markdown -I . \
    -m wagtail_streamfield_migration_toolkit.migrate_operation \
    -m wagtail_streamfield_migration_toolkit.operations \
    -m wagtail_streamfield_migration_toolkit.utils \
    --render-toc > docs/REFERENCE.md