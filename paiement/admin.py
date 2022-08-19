from django.contrib import admin
from .models import *

@admin.register(Frais)
class FraisAdmin(admin.ModelAdmin):
     ordering = ('-id',)
     list_display = ("id","type",)
     search_fields = ['type',] 

# Register your models here.
