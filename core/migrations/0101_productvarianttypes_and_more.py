# Generated by Django 4.2.4 on 2024-03-15 07:20

from django.db import migrations, models
import django.db.models.deletion
import shortuuid.django_fields


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0100_rename_pid_productvarient_pvid_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductVariantTypes",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "variant_title",
                    models.CharField(default="Product Varient", max_length=500),
                ),
                (
                    "varient_price",
                    models.DecimalField(decimal_places=2, default="1", max_digits=9999),
                ),
                (
                    "packaging_size",
                    models.CharField(default="Packaging Size", max_length=100),
                ),
                ("date", models.DateField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.product"
                    ),
                ),
            ],
            options={"verbose_name_plural": "Product Variant Types",},
        ),
        migrations.RemoveField(model_name="productvarient", name="description",),
        migrations.AlterField(
            model_name="productvarient",
            name="pvid",
            field=shortuuid.django_fields.ShortUUIDField(
                alphabet="abcdefgh12345",
                length=22,
                max_length=30,
                prefix="pvid",
                unique=True,
            ),
        ),
        migrations.DeleteModel(name="ProductVariantImages",),
        migrations.AddField(
            model_name="productvarianttypes",
            name="product_variant",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="core.productvarient"
            ),
        ),
    ]
