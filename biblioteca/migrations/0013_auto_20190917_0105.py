# Generated by Django 2.1.7 on 2019-09-17 01:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioteca', '0012_auto_20190917_0057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libro',
            name='Numero_Copie',
            field=models.IntegerField(default=5),
            preserve_default=False,
        ),
    ]
