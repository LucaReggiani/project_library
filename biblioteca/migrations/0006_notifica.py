# Generated by Django 2.1.7 on 2019-09-07 02:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('biblioteca', '0005_prestito_datarestituzione'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notifica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Descrizione', models.CharField(max_length=100)),
                ('ISBN10', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='biblioteca.Libro')),
            ],
        ),
    ]