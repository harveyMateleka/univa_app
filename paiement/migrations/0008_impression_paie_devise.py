# Generated by Django 3.2.8 on 2022-09-22 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paiement', '0007_impression_paie'),
    ]

    operations = [
        migrations.AddField(
            model_name='impression_paie',
            name='devise',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
