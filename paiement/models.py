from django.db import models
from parametrage.models import  Utilisat,annee,promotions

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
    tranche=models.CharField(max_length=10,blank=True, null=True)
    montant=models.DecimalField(max_digits=10,decimal_places=2,blank=True, null=True,default=0)
    devise=models.CharField(max_length=5,blank=True, null=True)
    fraistranche=models.ForeignKey(Fraisclasse, models.PROTECT,blank=True, null=True)



