# Generated by Django 3.0.2 on 2020-01-29 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AzadiApp', '0003_auto_20200129_1742'),
    ]

    operations = [
        migrations.AddField(
            model_name='watch',
            name='full_location',
            field=models.TextField(default=None, null=True),
        ),
    ]
