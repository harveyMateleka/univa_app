from django.urls import path, include
from .views import *
from . import views
app_name='cote'
urlpatterns = [

    path('exemplaire/', views.ExemplaireListView.as_view(permission_required='cote.view_exemplaire'),name='exemplaire'),
    path('exemplaire/<int:pk>/detail', views.ExemplaireDetailView.as_view(permission_required='cote.view_exemplaire'),name='exemplaire_detail'),
    path('exemplaire/create/', views.ExemplaireCreateView.as_view(permission_required='cote.add_exemplaire'),name='exemplaire_create'),
    path('exemplaire/<int:pk>/update/',views.ExemplaireUpdateView.as_view(permission_required='cote.change_exemplaire'), name='exemplaire_update'),
    path('exemplaire/<int:pk>/delete/',views.ExemplaireDeleteView.as_view(permission_required='cote.delete_exemplaire'), name='exemplaire_delete'),

    path('cote/', views.CoteListView.as_view(permission_required='cote.view_cote'),name='cote'),
    # path('cote/<int:pk>/detail', views.CoteDetailView.as_view(permission_required='cote.view_cote'),name='cote_detail'),
    # path('cote/create/', views.CoteCreateView.as_view(permission_required='cote.add_cote'),name='cote_create'),
    # path('cote/<int:pk>/update/',views.CoteUpdateView.as_view(permission_required='cote.change_cote'), name='cote_update'),
    # path('cote/<int:pk>/delete/',views.CoteDeleteView.as_view(permission_required='cote.delete_cote'), name='cote_delete'),

    path('deliberation/',deliberation, name='deliberation'),
    path('listdeliberation/',listdeliberation, name='listdeliberation'),
    path('listdeliberationone/',listdeliberationone, name='listdeliberationone'),

    path('addfile/',addfile, name='addfile'),
    path('corriger/',corriger, name='corriger'),
    path('deletefile/',deletefile, name='deletefile'),

]
