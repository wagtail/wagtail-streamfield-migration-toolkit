pydoc-markdown -I . \
    -m wagtail_streamfield_migration_toolkit.migrate_operation \
    -m wagtail_streamfield_migration_toolkit.operations \
    --render-toc > docs/REFERENCE.md