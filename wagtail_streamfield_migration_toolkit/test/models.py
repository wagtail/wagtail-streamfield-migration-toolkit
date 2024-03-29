from django.db import models
from wagtail.fields import StreamField
from wagtail.blocks import CharBlock, StreamBlock, StructBlock, ListBlock

from wagtail.models import Page


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
