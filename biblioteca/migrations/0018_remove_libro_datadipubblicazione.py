# Generated by Django 2.1.7 on 2019-09-17 13:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('biblioteca', '0017_auto_20190917_0123'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='libro',
            name='DataDiPubblicazione',
        ),
    ]