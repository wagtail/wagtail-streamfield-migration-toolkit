from statistics import mode
from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.blocks import CharBlock, StreamBlock, StructBlock


class StructBlock1(StructBlock):
    struct1field1 = CharBlock()
    struct1field2 = CharBlock()


class StreamBlock1(StreamBlock):
    stream1field1 = CharBlock()
    stream1field2 = CharBlock()


class BaseStreamBlock(StreamBlock):
    field1 = CharBlock()
    field2 = CharBlock()
    struct1 = StructBlock1()
    stream1 = StreamBlock1()


class SampleModel(models.Model):
    content = StreamField(BaseStreamBlock(), use_json_field=True)
