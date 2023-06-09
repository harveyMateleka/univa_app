# Generated by Django 3.2.13 on 2022-07-03 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parametrage', '0004_etudiants_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='etudiants',
            name='etat_civil',
            field=models.CharField(choices=[('C', 'Célibataire'), ('M', 'Marié')], default='C', max_length=20),
        ),
        migrations.AlterField(
            model_name='etudiants',
            name='sexe',
            field=models.CharField(choices=[('F', 'Feminin'), ('M', 'Masculin')], default='M', max_length=1),
        ),
    ]
