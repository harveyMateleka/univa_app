# Generated by Django 3.2.13 on 2022-07-16 16:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parametrage', '0005_auto_20220703_1603'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cote', '0004_auto_20220710_0043'),
    ]

    operations = [
        migrations.CreateModel(
            name='tempjournalcote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('lien', models.CharField(max_length=255)),
                ('obs', models.CharField(max_length=255)),
                ('matricule', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='parametrage.etudiants')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='cote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('lien', models.CharField(max_length=255)),
                ('numero', models.IntegerField(default=1)),
                ('cote', models.FloatField()),
                ('annee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='parametrage.annee')),
                ('cours', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='parametrage.cours')),
                ('matricule', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='parametrage.etudiants')),
                ('promotion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='parametrage.promotions')),
                ('sesionn', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='parametrage.sessions')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('matricule', 'promotion', 'cours', 'annee', 'sesionn', 'numero')},
            },
        ),
    ]
