# Generated by Django 4.2.4 on 2024-04-01 10:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0110_invoicenumber"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productvarianttypes",
            name="product",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.product",
            ),
        ),
    ]