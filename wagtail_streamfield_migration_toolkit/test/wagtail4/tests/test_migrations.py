from wagtail_streamfield_migration_toolkit.test.wagtail4 import models, factories
from wagtail_streamfield_migration_toolkit.test.tests.test_migrations import BaseMigrationTest


class TestNonPageModelWithRevisions(BaseMigrationTest):
    model = models.SampleModelWithRevisions
    factory = factories.SampleModelWithRevisionsFactory
    has_revisions = True
    app_name = "toolkit_wagtail4_test"

    def test_migrate_stream_data(self):
        self._test_migrate_stream_data()

    def test_migrate_revisions(self):
        self._test_migrate_revisions()

    def test_always_migrate_live_and_latest_revisions(self):
        self._test_always_migrate_live_and_latest_revisions()

    def test_migrate_revisions_from_date(self):
        self._test_migrate_revisions_from_date()
