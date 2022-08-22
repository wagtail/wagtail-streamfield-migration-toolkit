from django.db import models
from wagtail.fields import StreamField
from wagtail.blocks import CharBlock, StreamBlock, StructBlock, ListBlock

from wagtail_streamfield_migration_toolkit.utils import __wagtailversion3__

if __wagtailversion3__:
    from wagtail.models import Page
else:
    from wagtail.models import Page, RevisionMixin, DraftStateMixin


class SimpleStructBlock(StructBlock):
    char1 = CharBlock()
    char2 = CharBlock()


class SimpleStreamBlock(StreamBlock):
    char1 = CharBlock()
    char2 = CharBlock()


class NestedStructBlock(StructBlock):
    char1 = CharBlock()
    stream1 = SimpleStreamBlock()
    struct1 = SimpleStructBlock()
    list1 = ListBlock(CharBlock())


class NestedStreamBlock(StreamBlock):
    char1 = CharBlock()
    stream1 = SimpleStreamBlock()
    struct1 = SimpleStructBlock()
    list1 = ListBlock(CharBlock())


class BaseStreamBlock(StreamBlock):
    char1 = CharBlock()
    char2 = CharBlock()
    simplestruct = SimpleStructBlock()
    simplestream = SimpleStreamBlock()
    simplelist = ListBlock(CharBlock())
    nestedstruct = NestedStructBlock()
    nestedstream = NestedStreamBlock()
    nestedlist_struct = ListBlock(SimpleStructBlock())
    nestedlist_stream = ListBlock(SimpleStreamBlock())


class SampleModel(models.Model):
    content = StreamField(BaseStreamBlock(), use_json_field=True)


class SamplePage(Page):
    content = StreamField(BaseStreamBlock(), use_json_field=True)


if not __wagtailversion3__:

    class SampleModelWithRevisions(DraftStateMixin, RevisionMixin, models.Model):
        content = StreamField(BaseStreamBlock(), use_json_field=True)
