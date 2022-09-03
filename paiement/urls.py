from django.urls import path, include
from .views import *
app_name='paiement'
urlpatterns = [

    path('', check, name="check"),
    path('uncheck/', uncheck, name="uncheck"),
    path('home', TemplateMain.as_view(template_name='base.html'),name='home'),
    path('paiement_frais', Paiement_fraisView.as_view(),name='paiement_frais'),
    path('edit_frais_classe', getfrais,name='getfrais'),
    path('delete_frais',delete_frais,name='delete_frais'),
    path('paiements',Paiement_templateView.as_view(),name='get_paiements'),
    path('get_etudiant/<str:anne>,<str:promotion>',get_etudiant),
    path('get_tranche/<str:anne>,<str:promotion>,<str:frais>',get_tranche),
    path('get_montant',get_montant,name='get_montant'),
    path('delete_paie',delete_paie,name='delete_paie'),
    path('releve_paiement',Relevent.as_view(),name='releve_paiement'),
    path('get_releve/<str:anne>,<str:matricule>',get_releve),
    path('rapport_journalier',rapport_journalier,name='rapport_journalier'),
    path('get_rapportJ/<str:dates>,<str:frais>',get_rapportJ)
    
    
  
    #path('importation',edit_etudiant,name='edit_etudiant'),
    

]