# Generated by Django 4.2.4 on 2024-02-08 05:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0088_alter_product_old_price_alter_product_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvarient',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
