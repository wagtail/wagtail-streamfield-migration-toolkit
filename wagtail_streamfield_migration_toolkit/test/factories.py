import factory
from factory.django import DjangoModelFactory
import wagtail_factories

from . import models


class SimpleStructBlockFactory(wagtail_factories.StructBlockFactory):
    char1 = "Char Block 1"
    char2 = "Char Block 2"

    class Meta:
        model = models.SimpleStructBlock


# TODO SimpleStreamBlockFactory


class NestedStructBlockFactory(wagtail_factories.StructBlockFactory):
    char1 = "Char Block 1"
    struct1 = factory.SubFactory(SimpleStructBlockFactory)
    # stream1
    list1 = wagtail_factories.ListBlockFactory(wagtail_factories.CharBlockFactory)

    class Meta:
        model = models.NestedStructBlock


# TODO NestedStreamBlockFactory


class SampleModelFactory(DjangoModelFactory):
    content = wagtail_factories.StreamFieldFactory(
        {
            "char1": wagtail_factories.CharBlockFactory,
            "char2": wagtail_factories.CharBlockFactory,
            "simplestruct": SimpleStructBlockFactory,
            # TODO "simplestream"
            "simplelist": wagtail_factories.ListBlockFactory(
                wagtail_factories.CharBlockFactory
            ),
            "nestedstruct": NestedStructBlockFactory,
            # TODO "nestedstream"
            "nestedlist_struct": wagtail_factories.ListBlockFactory(
                SimpleStructBlockFactory
            ),
            # TODO "nestedlist_stream"
        }
    )

    class Meta:
        model = models.SampleModel
