# Generated by Django 2.1.7 on 2019-08-26 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioteca', '0002_auto_20190826_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prestito',
            name='DataPrenotazione',
            field=models.CharField(max_length=30),
        ),
    ]
