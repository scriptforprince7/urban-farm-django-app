# Generated by Django 4.2.4 on 2024-02-06 09:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0083_alter_product_specifications"),
    ]

    operations = [
        migrations.RemoveField(model_name="productvarient", name="updated",),
        migrations.RemoveField(model_name="productvarient", name="user",),
    ]
