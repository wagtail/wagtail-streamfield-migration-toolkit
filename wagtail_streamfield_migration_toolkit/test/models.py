from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.blocks import CharBlock, StreamBlock, StructBlock


class StructBlock1(StructBlock):
    struct1_char1 = CharBlock()
    struct1_char2 = CharBlock()
    struct1_stream1 = StreamBlock([
        ("struct1_stream1_char1", CharBlock()),
        ("struct1_stream1_char2", CharBlock())
    ])

class StreamBlock1(StreamBlock):
    stream1_char1 = CharBlock()
    stream1_char2 = CharBlock()


class BaseStreamBlock(StreamBlock):
    char1 = CharBlock()
    char2 = CharBlock()
    struct1 = StructBlock1()
    stream1 = StreamBlock1()


class SampleModel(models.Model):
    content = StreamField(BaseStreamBlock(), use_json_field=True)
