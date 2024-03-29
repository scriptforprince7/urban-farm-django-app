# Generated by Django 4.2.4 on 2024-03-14 09:55

from django.db import migrations
import shortuuid.django_fields


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0096_product_application_product_hsn_code_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="sku",
            field=shortuuid.django_fields.ShortUUIDField(
                alphabet="12345678900",
                length=22,
                max_length=11,
                prefix="sku",
                unique=True,
            ),
        ),
    ]
