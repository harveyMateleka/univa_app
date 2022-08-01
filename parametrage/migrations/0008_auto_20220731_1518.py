# Generated by Django 3.2.13 on 2022-07-31 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parametrage', '0007_auto_20220724_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='etudiants',
            name='date_naissance',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='etudiants',
            name='etat_civil',
            field=models.CharField(blank=True, choices=[('C', 'Célibataire'), ('M', 'Marié')], default='C', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='etudiants',
            name='prenom',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='etudiants',
            name='sexe',
            field=models.CharField(blank=True, choices=[('F', 'Feminin'), ('M', 'Masculin')], default='M', max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='etudiants',
            name='telephone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
