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

class Fixation(models.Model):
    anne=models.ForeignKey(annee, models.PROTECT,editable=True,blank=True, null=True)
    libelle= models.CharField(max_length=60,blank=True, null=True)
    montant=models.DecimalField(max_digits=8,decimal_places=2,blank=True, null=True,default=0)
    etat=models.BooleanField(default=False)
    devise=models.CharField(max_length=5,blank=True, null=True)

    def __str__(self):
        return self.libelle
class Paimentinscription(TimespantedModel):
    prix=models.ForeignKey(Fixation, models.PROTECT,blank=True, null=True)
    code_candi=models.CharField(max_length=25,blank=True, null=True)
    observation=models.CharField(max_length=60,blank=True, null=True)
    montant=models.DecimalField(max_digits=8,decimal_places=2,blank=True, null=True,default=0)
    indice=models.CharField(max_length=1,blank=True, null=True,default="0")

    def __str__(self):
        return self.code_candi
class Candidat(TimespantedModel):
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
    reussie=models.CharField(max_length=1, blank=True, null=True,default="0")
    code=models.ForeignKey(Paimentinscription, models.PROTECT,editable=True,blank=True, null=True)
    
    def __str__(self):
        return self.nom

class Dossier(models.Model):
    candidat=models.ForeignKey(Candidat, models.PROTECT,blank=True, null=True)
    dossierss=models.ImageField(upload_to='img_candidat/',default=None,blank=True)

class Testadmin(models.Model):
     candidat=models.ForeignKey(Candidat, models.PROTECT,blank=True, null=True,related_name='candidatest')
     classe=models.ForeignKey(promotions, models.PROTECT,blank=True, null=True,related_name='codpromo')
     anne=models.ForeignKey(annee, models.PROTECT,blank=True, null=True)






