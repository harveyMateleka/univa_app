from django.db import models
from parametrage.models import  Utilisat,annee,promotions,etudiants

# Create your models here.
class TimespantedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract=True
class Frais(models.Model):
    type=models.CharField(max_length=30,unique=True,blank=True,null=True) 

    def __str__(self):
        return self.type

class Fraisclasse(TimespantedModel):
    anne=models.ForeignKey(annee, models.PROTECT,blank=True, null=True)
    promotion=models.ForeignKey(promotions, models.PROTECT,blank=True, null=True,related_name='codpromos')
    frais=models.ForeignKey(Frais, models.PROTECT,blank=True, null=True,related_name='fraiscl')
    devise=models.CharField(max_length=5,blank=True, null=True)
    montant=models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True,default=0)

class Fraistranche(TimespantedModel):
    tranche=models.CharField(max_length=20,blank=True, null=True)
    montant=models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True,default=0)
    devise=models.CharField(max_length=5,blank=True, null=True)
    fraistranche=models.ForeignKey(Fraisclasse, models.PROTECT,blank=True, null=True)

class Paiement_frais(TimespantedModel):
    code_paie= models.CharField(max_length=20,blank=True, null=True,unique=True)
    matricule=models.ForeignKey(etudiants, models.PROTECT,blank=True, null=True,related_name='paie_etudiant')
    tranche=models.ForeignKey(Fraistranche, models.PROTECT,blank=True, null=True,related_name='paie_tranche')
    anne=models.ForeignKey(annee, models.PROTECT,blank=True, null=True)
    montantpaie=models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True,default=0)
    user=models.ForeignKey(Utilisat, models.PROTECT,blank=True, null=True) 
    frais=models.ForeignKey(Frais, models.PROTECT,blank=True, null=True)

class Impression_paie(models.Model):
    dateOp =models.DateField(blank=True, null=True)
    code_paie= models.CharField(max_length=20,blank=True, null=True,unique=True)
    montlettre = models.CharField(max_length=255,blank=True, null=True)
    totalfrais = models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True,default=0)
    totalreste = models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True,default=0)
    totalpaye = models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True,default=0)
    totaltranche = models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True,default=0)
    montantpaie=models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True,default=0)
    frais=models.ForeignKey(Frais, models.PROTECT,blank=True, null=True)
    user=models.ForeignKey(Utilisat, models.PROTECT,blank=True, null=True)
    matricule=models.ForeignKey(etudiants, models.PROTECT,blank=True, null=True,related_name='paie_etudiants')
    anne=models.ForeignKey(annee, models.PROTECT,blank=True, null=True) 
    promotion=models.ForeignKey(promotions, models.PROTECT,blank=True, null=True,related_name='promotions')
    devise=models.CharField(max_length=5,blank=True, null=True)
    tranche=models.ForeignKey(Fraistranche, models.PROTECT,blank=True, null=True,related_name='paie_tranches')



