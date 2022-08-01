from django.contrib import admin
from .models import enseigne
# Register your models here.
@admin.register(enseigne)
class enseigneAdmin(admin.ModelAdmin):
    ordering = ('-created_at',)
    list_display = ("id","user","promotion","annee","cours","ponderaton","heure","categorie","etat")
    exclude = ('tp','interro')
    autocomplete_fields = ['user',"promotion","annee","cours"]
    list_display_links =  ['id','user',"promotion","annee","cours"]
    search_fields = ['user', ]