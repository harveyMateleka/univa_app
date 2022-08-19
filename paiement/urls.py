from django.urls import path, include
from .views import *
app_name='paiement'
urlpatterns = [

    path('', check, name="check"),
    path('uncheck/', uncheck, name="uncheck"),
    path('home', TemplateMain.as_view(template_name='base.html'),name='home'),
    path('paiement_frais', Paiement_fraisView.as_view(),name='paiement_frais'),
  
    #path('importation',edit_etudiant,name='edit_etudiant'),
    

]