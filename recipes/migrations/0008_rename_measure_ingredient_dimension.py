# Generated by Django 3.2.3 on 2021-06-09 09:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20210609_1201'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='measure',
            new_name='dimension',
        ),
    ]