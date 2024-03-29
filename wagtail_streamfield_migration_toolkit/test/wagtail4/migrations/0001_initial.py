# Generated by Django 4.0.3 on 2022-09-02 03:18

from django.db import migrations, models
import django.db.models.deletion
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0076_modellogentry_revision'),
        ('toolkit_test', '0001_initial')
    ]

    operations = [
        migrations.CreateModel(
            name='SampleModelWithRevisions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('live', models.BooleanField(default=True, editable=False, verbose_name='live')),
                ('has_unpublished_changes', models.BooleanField(default=False, editable=False, verbose_name='has unpublished changes')),
                ('first_published_at', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='first published at')),
                ('last_published_at', models.DateTimeField(editable=False, null=True, verbose_name='last published at')),
                ('go_live_at', models.DateTimeField(blank=True, null=True, verbose_name='go live date/time')),
                ('expire_at', models.DateTimeField(blank=True, null=True, verbose_name='expiry date/time')),
                ('expired', models.BooleanField(default=False, editable=False, verbose_name='expired')),
                ('content', wagtail.fields.StreamField([('char1', wagtail.blocks.CharBlock()), ('char2', wagtail.blocks.CharBlock()), ('simplestruct', wagtail.blocks.StructBlock([('char1', wagtail.blocks.CharBlock()), ('char2', wagtail.blocks.CharBlock())])), ('simplestream', wagtail.blocks.StreamBlock([('char1', wagtail.blocks.CharBlock()), ('char2', wagtail.blocks.CharBlock())])), ('simplelist', wagtail.blocks.ListBlock(wagtail.blocks.CharBlock())), ('nestedstruct', wagtail.blocks.StructBlock([('char1', wagtail.blocks.CharBlock()), ('stream1', wagtail.blocks.StreamBlock([('char1', wagtail.blocks.CharBlock()), ('char2', wagtail.blocks.CharBlock())])), ('struct1', wagtail.blocks.StructBlock([('char1', wagtail.blocks.CharBlock()), ('char2', wagtail.blocks.CharBlock())])), ('list1', wagtail.blocks.ListBlock(wagtail.blocks.CharBlock()))])), ('nestedstream', wagtail.blocks.StreamBlock([('char1', wagtail.blocks.CharBlock()), ('stream1', wagtail.blocks.StreamBlock([('char1', wagtail.blocks.CharBlock()), ('char2', wagtail.blocks.CharBlock())])), ('struct1', wagtail.blocks.StructBlock([('char1', wagtail.blocks.CharBlock()), ('char2', wagtail.blocks.CharBlock())])), ('list1', wagtail.blocks.ListBlock(wagtail.blocks.CharBlock()))])), ('nestedlist_struct', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('char1', wagtail.blocks.CharBlock()), ('char2', wagtail.blocks.CharBlock())]))), ('nestedlist_stream', wagtail.blocks.ListBlock(wagtail.blocks.StreamBlock([('char1', wagtail.blocks.CharBlock()), ('char2', wagtail.blocks.CharBlock())])))], use_json_field=True)),
                ('latest_revision', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.revision', verbose_name='latest revision')),
                ('live_revision', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.revision', verbose_name='live revision')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
