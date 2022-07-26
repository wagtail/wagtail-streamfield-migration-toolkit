# flake8: NOQA
from .migrate_operation import MigrateStreamData

default_app_config = "wagtail_streamfield_migration_toolkit.apps.WagtailStreamfieldMigrationToolkitAppConfig"


VERSION = (0, 1, 0)
__version__ = ".".join(map(str, VERSION))
