# Generated by Django 5.1.2 on 2024-10-24 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_dr', '0002_alter_user_options_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teste',
            name='tempo',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
