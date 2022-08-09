from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Fixation)
class FixationAdmin(admin.ModelAdmin):
    ordering = ('-id',)
    list_display = ("id","libelle","montant","anne")
    search_fields = ['libelle','anne' ]
