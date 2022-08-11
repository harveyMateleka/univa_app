# Generated by Django 3.2.8 on 2022-08-10 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0006_fixation_paimentinscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='paimentinscription',
            name='montant',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, null=True),
        ),
    ]