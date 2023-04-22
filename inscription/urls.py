from django.urls import path, include
from .views import *
from . import views
app_name='inscription'

urlpatterns = [

    path('', check, name="check"),
    path('uncheck/', uncheck, name="uncheck"),
    path('home', TemplateMain.as_view(template_name='base.html'),name='home'),
    path('liste_candidat', CandidatListView.as_view(),name='listes_candidats'),
    path('candidat', CandidatsView.as_view(),name='candidats'),
    path('create', CandidatsView.as_view(),name='creates'),
    path('liste_par_anne/<str:anne>,<str:promotion>', get_candidat),
    path('paiement', Paiement.as_view(),name='paiement'),
    path('getpaiement',getpaiement,name='getpaiement'),
    path('getpaiement_all',getpaiement_all,name='getpaiement_all'),
    path('get_id_candidat/<str:id>',get_id_candidat),
    path('edit_etudiant',edit_etudiant,name='edit_etudiant'),
    path('desactive_candidat',desapprov,name='desapprov'),
    path('liste_candi_inactif',get_candidat_inactif,name='get_candidat_inactif'),
    path('index_inactif',index_inactif,name='index_inactif'),
    path('index_statistique',statistique_C,name='statistique_C'),
    path('statistique_candidat/<str:anne>,<str:valeur>',statique_candidat),
    path('imprimer_statistique',imprime_statistique,name="imprime_statistique"),
    path('imprimer_statistique_R',imprime_statistique_r,name="imprime_statistique_r"),
    path('imprime_inactif',imprime_inactif,name="imprime_inactif"),
    path('liste_candidats',liste_candidat,name="liste_candidats"),
    path('delete_paie_inscription',destroy_paie,name="delete_paie_candi"),
    
    #path('importation',edit_etudiant,name='edit_etudiant'),
    

]