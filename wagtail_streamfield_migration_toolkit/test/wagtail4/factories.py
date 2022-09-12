from factory.django import DjangoModelFactory
import wagtail_factories

from . import models
from wagtail_streamfield_migration_toolkit.test.factories import BaseStreamBlockFactory


class SampleModelWithRevisionsFactory(DjangoModelFactory):
    content = wagtail_factories.StreamFieldFactory(BaseStreamBlockFactory)

    class Meta:
        model = models.SampleModelWithRevisions
