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

]