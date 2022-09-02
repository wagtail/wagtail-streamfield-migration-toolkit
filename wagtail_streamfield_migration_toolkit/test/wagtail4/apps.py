from django.apps import AppConfig


class Wagtail4TestsConfig(AppConfig):
    label = "toolkit_wagtail4_test"
    name = "wagtail_streamfield_migration_toolkit.test.wagtail4"
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = "Wagtail streamfield-migration-toolkit tests wagtail4"
