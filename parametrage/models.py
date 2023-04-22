from django.contrib.auth.models import User, AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q

sessions = (
    ("1","Mi-Session"),
    ("2","1ere Session"),
    ("3","2eme Session"),
    ("5","Interro"),
    ("4","Tp"),
    ("6","Session Special"),
    )

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



class Utilisat(AbstractUser):
    sexe = models.CharField(choices=Sexe, max_length=255)

class universite(TimespantedModel):
    pays = models.CharField(max_length=50)
    ministere=models.CharField(max_length=255,default="Ministere de l'Enseignement Superieur et Universitaire")
    ville = models.CharField(max_length=50)
    commune = models.CharField(max_length=50)
    nom = models.CharField(max_length=255)
    sigle = models.CharField(max_length=50)
    siteweb = models.CharField(max_length=50)
    upload=models.ImageField(upload_to='logo_images',blank=True,null=True)
    def __str__(self):
        return self.nom
    class Meta:
        verbose_name = 'Univesité'
        verbose_name_plural = 'Univesités'

class annee(TimespantedModel):
    libelle = models.CharField(max_length=9,unique=True)
    etat = models.BooleanField(default=False)
    def __str__(self):
        return self.libelle
    class Meta:
        verbose_name = 'Annee'
        verbose_name_plural = 'Annees'

# class sessions(TimespantedModel):
#     libelle = models.CharField(max_length=100)
#     etat = models.BooleanField(default=True)
#     def __str__(self):
#         return self.libelle
#     class Meta:
#         verbose_name = 'Session'
#         verbose_name_plural = 'Sessions'


class departements(TimespantedModel):
    libelle = models.CharField(max_length=100)
    etat = models.BooleanField(default=True)
    def __str__(self):
        return self.libelle
    class Meta:
        verbose_name = 'Departement'
        verbose_name_plural = 'Departements'

class sections(TimespantedModel):
    libelle = models.CharField(max_length=100)
    departement = models.ForeignKey(departements, models.PROTECT)
    etat = models.BooleanField(default=True)
    def __str__(self):
        return self.libelle
    class Meta:
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'

class options(TimespantedModel):
    libelle = models.CharField(max_length=100)
    section = models.ForeignKey(sections, models.PROTECT)
    etat = models.BooleanField(default=True)
    def __str__(self):
        return self.libelle
    class Meta:
        verbose_name = 'Option'
        verbose_name_plural = 'Options'

class promotions(TimespantedModel):
    libelle = models.CharField(max_length=100)
    option = models.ForeignKey(options, models.PROTECT)
    etat = models.BooleanField(default=True)
    type= models.IntegerField(default=0)
    def __str__(self):
        return self.libelle
    class Meta:
        verbose_name = 'Promotion'
        verbose_name_plural = 'Promotions'

class cours(TimespantedModel):
    libelle = models.CharField(max_length=255,unique=True)
    sigle = models.CharField(max_length=10,unique=True)
    etat = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle
    class Meta:
        verbose_name = 'Cours'
        verbose_name_plural = 'Cours'

class etudiants(TimespantedModel):
    matricule = models.CharField(max_length=50,unique=True)
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

    def __str__(self):
        return self.nom



class Droit(models.Model):
    class Meta:
        permissions=(
            # ('cotation','Onglet Cotation'),

            # # ('rapport','Onglet Rapport'),
            # ('validation','Validateur'),
            # ('inscrit','Etudiant Valide'),
            # # ('paiement','Onglet Paiement'),
            # # ('presence','Onglet Presence'),
            # # ('depense','Onglet Depense'),
            # # ('conge','Onglet Conge'),
            # # ('rh','Onglet RH'),
            # # ('evaluation','Onglet Evaluation'),
            # # ('tableau','Onglet Tableau'),
            # ('noteobtenue','Onglet Note obtenue acad.'),
            # ('noteobtenueetudiant','Onglet Note obtenue Etud.'),
            #
            #
            # ('tablobord','Menu tableau de Bord'),
            # ('apropoetu','Menu Etudiant profil'),
            # ('apropoprof','Menu Professeur profil'),
            #
            # ('listetud','Menu liste Etudiant'),
            # ('listetudordre','Menu liste Etudiant ordre'),
            # ('listetudlitige','Menu liste Etudiant litige'),
            # ('inscrits','Menu Etudiant inscrit'),
            # ('noninscrits','Menu  Etudiant en cours inscription'),
            # ('nonconforme','Menu Etudiant inscrit non conform'),
            #
            # ('programme','Menu Programme'),
            # ('emailling','Menu Emailling'),
            # ('grh','Menu Gestion RH'),
            # ('etudiants','Menu Etudiant'),
            # ('rap','Menu Rapport'),
            # ('archivage','Menu Archivages'),
            # ('bibliotheque','Menu Biblioteque'),
            # ('finance','Menu Finances'),




        )
# class UserPermission(models.Model):
#     id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
#     userid = models.ForeignKey('Utilisateur', models.DO_NOTHING, db_column='UserId', blank=True, null=True)  # Field name made lowercase.
#     permissionid = models.ForeignKey(Permission, models.DO_NOTHING, db_column='PermissionId', blank=True, null=True)  # Field name made lowercase.
#     active = models.BooleanField(db_column='Active', blank=True, null=True)  # Field name made lowercase.
#
#     class Meta:
#         managed = True
#         db_table = 'USER_PERMISSION'
#
#
# class Utilisateur(models.Model):
#     utilisateur_id = models.AutoField(db_column='Utilisateur_Id', primary_key=True)  # Field name made lowercase.
#     utilisateur_prenom = models.CharField(db_column='Utilisateur_Prenom', max_length=150, blank=True, null=True)  # Field name made lowercase.
#     utilisateur_login = models.CharField(db_column='Utilisateur_Login', max_length=150, blank=True, null=True)  # Field name made lowercase.
#     utilisateurspassword = models.CharField(db_column='UtilisateursPassword', max_length=150, blank=True, null=True)  # Field name made lowercase.
#     utilisateur_nomcomplet = models.CharField(db_column='utilisateur_NomComplet', max_length=150, blank=True, null=True)  # Field name made lowercase.
#     utilisateur_valide = models.BooleanField(db_column='Utilisateur_Valide', blank=True, null=True)  # Field name made lowercase.
#     utilisateur_date_creation = models.DateField(db_column='Utilisateur_Date_Creation', blank=True, null=True)  # Field name made lowercase.
#     roleid = models.ForeignKey(Roles, models.DO_NOTHING, db_column='RoleId', blank=True, null=True)  # Field name made lowercase.
#     adresse = models.CharField(db_column='Adresse', max_length=255, blank=True, null=True)  # Field name made lowercase.
#     telephone = models.CharField(db_column='Telephone', max_length=15, blank=True, null=True)  # Field name made lowercase.
#     email = models.CharField(db_column='Email', max_length=25, blank=True, null=True)  # Field name made lowercase.
#     isdeleted = models.BooleanField(db_column='IsDeleted', blank=True, null=True)  # Field name made lowercase.
#
#     class Meta:
#         managed = True
#         db_table = 'UTILISATEUR'
