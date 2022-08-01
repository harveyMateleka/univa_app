from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from parametrage.models import promotions,annee,etudiants,TimespantedModel,cours,Utilisat,sessions
# Create your models here.

categorie = (
    (1,"Matières de formation professionnelle"),
    (2,"Matières d'appui formation professionnelle"),
    (3,"Matières de formation générale"),

    )
class etudprom(TimespantedModel):
    matricule = models.ForeignKey(etudiants, models.PROTECT)
    promotion = models.ForeignKey(promotions, models.PROTECT)
    annee = models.ForeignKey(annee, models.PROTECT)
    mi_session = models.IntegerField(default=1)
    mention_mi_session = models.CharField(max_length=100, blank=True, null=True)
    pourc_mi_session = models.FloatField(blank=True, null=True)
    one_session = models.IntegerField(default=2)
    mention_one_session = models.CharField(max_length=100, blank=True, null=True)
    pourc_one_session = models.FloatField(blank=True, null=True)
    two_session = models.IntegerField(default=3)
    mention_two_session = models.CharField(max_length=100, blank=True, null=True)
    pourc_two_session = models.FloatField(blank=True, null=True)
    trav = models.FloatField(blank=True, null=True)
    stag = models.FloatField(blank=True, null=True)

    class Meta:
       unique_together=['matricule', 'promotion','annee']

class exemplaire(TimespantedModel):
    matricule = models.ForeignKey(etudiants, models.PROTECT)
    lien=models.CharField(max_length=255)
    user = models.ForeignKey(Utilisat, models.PROTECT)
    promotion = models.ForeignKey(promotions, models.PROTECT)
    annee = models.ForeignKey(annee, models.PROTECT)
    cours = models.ForeignKey(cours, models.PROTECT)
    sesionn = models.CharField(choices=sessions,max_length=1)
    numero = models.IntegerField(default=1)

    class Meta:
        unique_together=['matricule', 'promotion','cours','annee','sesionn','numero']

class cote(TimespantedModel):
    matricule = models.ForeignKey(etudiants, models.PROTECT)
    lien=models.CharField(max_length=255,null=True,blank=True)
    user = models.ForeignKey(Utilisat, models.PROTECT)
    promotion = models.ForeignKey(promotions, models.PROTECT)
    annee = models.ForeignKey(annee, models.PROTECT)
    cours = models.ForeignKey(cours, models.PROTECT)
    sesionn = models.CharField(choices=sessions,max_length=1)
    numero = models.IntegerField(default=1)
    cote = models.FloatField()



    class Meta:
        unique_together=['matricule', 'promotion','cours','annee','sesionn','numero']

class delibe(TimespantedModel):
    opde = models.CharField(max_length=5)
    de = models.FloatField()
    opa = models.CharField(max_length=5)
    a = models.FloatField()
    etat= models.CharField(max_length=10)
    op= models.CharField(max_length=5)
    nbr= models.IntegerField()
    position= models.IntegerField()

    class Meta:
        verbose_name = 'Règle Déliberation'
        verbose_name_plural = 'Règle Déliberation'
        unique_together=['opde', 'de','opa','a','etat','op','nbr','position']

class delibedetail(TimespantedModel):
    annee = models.ForeignKey(annee, models.PROTECT)
    dateop = models.DateField()
    president = models.CharField(max_length=255)
    secretaire1 = models.CharField(max_length=255)
    secretaire2 = models.CharField(max_length=255)
    membres = models.CharField(max_length=255)


class tempjournalcote(TimespantedModel):
    matricule = models.ForeignKey(etudiants, models.PROTECT)
    lien=models.CharField(max_length=255)
    obs=models.CharField(max_length=255)
    user = models.ForeignKey(Utilisat, models.PROTECT)

class enseigne(TimespantedModel):
    user = models.ForeignKey(Utilisat, models.PROTECT)
    promotion = models.ForeignKey(promotions, models.PROTECT)
    annee = models.ForeignKey(annee, models.PROTECT)
    cours = models.ForeignKey(cours, models.PROTECT)
    ponderaton = models.IntegerField()
    heure = models.IntegerField()
    tp = models.IntegerField(default=0)
    interro = models.IntegerField(default=0)
    categorie = models.IntegerField(choices=categorie,default=1)
    etat=models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Prof. Cours'
        verbose_name_plural = 'Prof. Cours'
        unique_together=['user', 'promotion','cours','annee']

# @receiver(post_save, sender=enseigne)
# def create_etud_prom(sender,instance, **kwargs):
#     if kwargs['created']:
#         pass
#     print(kwargs)

class Droit(models.Model):
    class Meta:
        permissions = (
            ('cotation', 'Menu Cotation'),
            ('transmission', 'Sous Menu Transmission - Cotation'),
            ('deliberation', 'Sous Menu Deliberation - Cotation'),

        )
