from django.db import models
from parametrage.models import Utilisat,annee,promotions

# Create your models here.
class TimespantedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True

Sexe = (
    ("F","Feminin"),
    ("M","Masculin")
    )
Etatcivil = (
    ("C","Célibataire"),
    ("M","Marié")
    )

class Candidat(TimespantedModel):
    code_candidat = models.CharField(max_length=50,unique=True)
    nom = models.CharField(max_length=50)
    postnom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50,blank=True, null=True)
    sexe = models.CharField(choices=Sexe,max_length=1,default='M',blank=True, null=True)
    etat_civil = models.CharField(choices=Etatcivil, max_length=20,default='C',blank=True, null=True)
    telephone = models.CharField(max_length=15,blank=True, null=True)
    adresse = models.CharField(max_length=155, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    date_naissance = models.DateField(blank=True, null=True)
    lieu_naissance = models.CharField(max_length=100, blank=True, null=True)
    etat = models.BooleanField(default=True)
    user=models.ForeignKey(Utilisat, models.PROTECT,blank=True, null=True)
    anne=models.ForeignKey(annee, models.PROTECT,blank=True, null=True)
    def __str__(self):
        return self.nom

class Dossier(models.Model):
    candidat=models.ForeignKey(Candidat, models.PROTECT,blank=True, null=True)
    dossier=models.ImageField(upload_to='img_candidat/',default=None,blank=True)

class Testadmin(models.Model):
     candidat=models.ForeignKey(Candidat, models.PROTECT,blank=True, null=True)
     classe=models.ForeignKey(promotions, models.PROTECT,blank=True, null=True)
