# Generated by Django 4.2.4 on 2024-03-05 06:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0094_alter_product_description_and_more"),
    ]

    operations = [
        migrations.RemoveField(model_name="architectureimages", name="architecture",),
        migrations.RemoveField(model_name="company_name", name="category",),
        migrations.RemoveField(model_name="company_name", name="maincat",),
        migrations.RemoveField(model_name="company_name", name="sub_category",),
        migrations.RemoveField(model_name="company_name", name="user",),
        migrations.RemoveField(model_name="sub_categories", name="category",),
        migrations.RemoveField(model_name="sub_categories", name="maincat",),
        migrations.RemoveField(model_name="sub_categories", name="user",),
        migrations.RemoveField(model_name="subcategoryimages", name="sub_category",),
        migrations.RemoveField(model_name="product", name="company_name",),
        migrations.RemoveField(model_name="product", name="sub_category",),
        migrations.DeleteModel(name="Architecture",),
        migrations.DeleteModel(name="ArchitectureImages",),
        migrations.DeleteModel(name="Company_name",),
        migrations.DeleteModel(name="Sub_categories",),
        migrations.DeleteModel(name="SubcategoryImages",),
    ]
