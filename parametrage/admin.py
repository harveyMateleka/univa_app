from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from cote.models import delibe
from .models import *


@admin.register(universite)
class universiteAdmin(admin.ModelAdmin):
    ordering = ('-created_at',)
    list_display = ("id","nom","sigle","commune","ville","pays","siteweb")
    list_display_links =  ['id','nom',"sigle" ]
    search_fields = ['nom',"sigle" ]

@admin.register(annee)
class anneeAdmin(admin.ModelAdmin):
    ordering = ('-created_at',)
    list_display = ("id","libelle","etat")
    list_display_links =  ['id','libelle' ]
    search_fields = ['libelle', ]

@admin.register(delibe)
class delibeAdmin(admin.ModelAdmin):
    ordering = ('opde',)
    list_display = ('opde', 'de','opa','a','etat','op','nbr','position')
    list_display_links =  ['opde', 'de','opa','a','etat','op','nbr','position']
    search_fields = ['opde', 'de','opa','a','etat','op','nbr' ]

# @admin.register(sessions)
# class sessionsAdmin(admin.ModelAdmin):
#     ordering = ('-created_at',)
#     list_display = ("id","libelle","etat")
#     list_display_links =  ['id','libelle' ]
#     search_fields = ['libelle', ]


@admin.register(departements)
class departementsAdmin(admin.ModelAdmin):
    ordering = ('-created_at',)
    list_display = ("id","libelle","etat")
    list_display_links =  ['id','libelle' ]
    search_fields = ['libelle', ]

@admin.register(sections)
class sectionsAdmin(admin.ModelAdmin):
    ordering = ('-created_at',)
    autocomplete_fields = ['departement', ]
    list_display = ("id","libelle","departement","etat")
    list_display_links =  ['id','libelle',"departement" ]
    search_fields = ['libelle', ]


@admin.register(options)
class optionsAdmin(admin.ModelAdmin):
    ordering = ('-created_at',)
    autocomplete_fields = ['section', ]
    list_display = ("id","libelle","section","etat")
    list_display_links =  ['id','libelle',"section" ]
    search_fields = ['libelle', ]


@admin.register(promotions)
class promotionsAdmin(admin.ModelAdmin):
    ordering = ('-created_at',)
    autocomplete_fields = ['option', ]
    list_display = ("id","libelle","option","etat")
    list_display_links =  ['id','libelle',"option" ]
    search_fields = ['libelle', ]


@admin.register(cours)
class coursAdmin(admin.ModelAdmin):
    ordering = ('-created_at',)
    list_display = ("id","libelle","sigle","etat")
    list_display_links =  ['id','libelle',"sigle" ]
    search_fields = ['libelle','sigle' ]


class UtilisatAdmin(UserAdmin):
    list_display = (
        'username', 'first_name', 'last_name', 'is_staff',
        'email','sexe'
    )

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email','sexe')
        }),
        # ('Affecations', {
        #     'fields': (
        #         'affectation',
        #     )
        # }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        # ('Additional info', {
        #     'fields': ('add1', 'add1', 'add1')
        # })
    )

    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email','sexe')
        }),
        # ('Affecations', {
        #     'fields': (
        #         'affectation',
        #     )
        # }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        # ('Additional info', {
        #     'fields': ('add1', 'add1', 'add1')
        # })
    )

admin.site.register(Utilisat, UtilisatAdmin)

#
# @admin.register(CategorieProduit)
# class CategorieProduitAdmin(admin.ModelAdmin):
#     ordering = ('libelle',)
#     list_display = ("id","libelle")
#     search_fields = ['libelle']
#     def save_model(self, request, obj, form, change):
#         if not obj.created_by:
#             obj.created_by = request.user
#         obj.save()
#
#
# @admin.register(Client)
# class ClientAdmin(admin.ModelAdmin):
#     ordering = ('nom',)
#     list_display = ("id","nom","telephone","adresse")
#     search_fields = ['nom']
#     def save_model(self, request, obj, form, change):
#         if not obj.created_by:
#             obj.created_by = request.user
#         obj.save()


