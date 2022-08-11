# Generated by Django 3.2.8 on 2022-08-11 12:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inscription', '0007_paimentinscription_montant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidat',
            name='code_candidat',
        ),
        migrations.AddField(
            model_name='candidat',
            name='code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='inscription.paimentinscription'),
        ),
    ]
