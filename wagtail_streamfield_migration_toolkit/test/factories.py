import factory
import wagtail_factories

try:
    from factory.django import DjangoModelFactory
except ImportError:
    from factory import DjangoModelFactory

from . import models


class SimpleStructBlockFactory(wagtail_factories.StructBlockFactory):
    char1 = "Char Block 1"
    char2 = "Char Block 2"

    class Meta:
        model = models.SimpleStructBlock

class SampleModelFactory(DjangoModelFactory):
    content = wagtail_factories.StreamFieldFactory({
        "char1": wagtail_factories.CharBlockFactory,
        "char2": wagtail_factories.CharBlockFactory,
        "simplestruct": SimpleStructBlockFactory
    })

    class Meta:
        model = models.SampleModel