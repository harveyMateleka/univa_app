from django.urls import path, include
from .views import *
from . import views
app_name='inscription'

urlpatterns = [

    path('', check, name="check"),
    path('uncheck/', uncheck, name="uncheck"),
    path('home', TemplateMain.as_view(template_name='base.html'),name='home'),
    path('liste_candidat', CandidatListView.as_view(),name='listes_candidats'),

]