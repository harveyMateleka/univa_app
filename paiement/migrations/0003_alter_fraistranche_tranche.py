# Generated by Django 3.2.8 on 2022-08-20 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paiement', '0002_fraistranche'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fraistranche',
            name='tranche',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
