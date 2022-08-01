from django.urls import path, include
from .views import *
from . import views
app_name='parametrage'




urlpatterns = [

    path('', check, name="check"),
    path('uncheck/', uncheck, name="uncheck"),
    path('home', TemplateMain.as_view(template_name='base.html'),name='home'),

    path('etudiants/', views.EtudiantsListView.as_view(permission_required='parametrage.view_etudiants'), name='etudiants'),
    path('etudiants/<int:pk>/detail', views.EtudiantsDetailView.as_view(permission_required='parametrage.view_etudiants'),name='etudiants_detail'),
    path('etudiants/create/', views.EtudiantsCreateView.as_view(permission_required='parametrage.add_etudiants'),name='etudiants_create'),
    path('etudiants/<int:pk>/update/', views.EtudiantsUpdateView.as_view(permission_required='parametrage.change_etudiants'), name='etudiants_update'),
    path('etudiants/<int:pk>/delete/', views.EtudiantsDeleteView.as_view(permission_required='parametrage.delete_etudiants'),name='etudiants_delete'),




]
