# Generated by Django 4.2.4 on 2024-03-15 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0098_remove_main_category_icon_img_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="main_category",
            name="description",
            field=models.CharField(default="N/A", max_length=500),
        ),
    ]