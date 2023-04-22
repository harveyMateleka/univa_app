from django.urls import path, include
from .views import *
app_name='paiement'
urlpatterns = [

    path('', check, name="check"),
    path('uncheck/', uncheck, name="uncheck"),
    path('home', TemplateMain.as_view(template_name='base.html'),name='home'),
    path('paiement_frais', Paiement_fraisView.as_view(),name='paiement_frais'),
    path('edit_frais_classe', getfrais,name='getfrais'),
    path('paiements',Paiement_templateView.as_view(),name='get_paiements'),
    path('get_etudiant/<str:anne>,<str:promotion>',get_etudiant),
    path('get_tranche/<str:anne>,<str:promotion>,<str:frais>',get_tranche),
    path('get_montant',get_montant,name='get_montant'),
    path('delete_paie',delete_paie,name='delete_paie'),
    path('releve_paiement',Relevent.as_view(),name='releve_paiement'),
    path('delete_frais_classe',delete_frais_classe,name='delete_frais_classe'),
    path('get_releve/<str:anne>,<str:matricule>',get_releve),
    path('rapport_journalier',rapport_journalier,name='rapport_journalier'),
    path('get_rapportJ/<str:dates>,<str:datess>',get_rapportJ),
    path('liste_frais_classe',liste_frais,name='liste_frais'),
    path('liste_detail',liste_detail,name='liste_detail'),
    path('get_imprimer/<str:var_id>',get_imprimer),
    path('impression_situaation',print_situation,name="print_situation")
    
    

]