from django.db import models
from wagtail.models import RevisionMixin, DraftStateMixin
from wagtail.fields import StreamField

from wagtail_streamfield_migration_toolkit.test.models import BaseStreamBlock


class SampleModelWithRevisions(DraftStateMixin, RevisionMixin, models.Model):
    content = StreamField(BaseStreamBlock(), use_json_field=True)
