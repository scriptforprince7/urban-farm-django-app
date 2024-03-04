# Generated by Django 4.2.4 on 2023-12-08 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0067_remove_sub_categories_canonical_link_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sub_categories',
            name='canonical_link',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sub_categories',
            name='meta_description',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sub_categories',
            name='meta_robots',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sub_categories',
            name='meta_tag',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sub_categories',
            name='meta_title',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sub_categories',
            name='og_description',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sub_categories',
            name='og_image',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sub_categories',
            name='og_title',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sub_categories',
            name='og_url',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sub_categories',
            name='twitter_description',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sub_categories',
            name='twitter_title',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='SubcategorySeo',
        ),
    ]
