from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from .models import *
from parametrage.models import annee,promotions
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages

# Create your views here.

class TemplateMain(LoginRequiredMixin,TemplateView):
    pass

def check(request):

    if request.user.username:
         return redirect(reverse('parametrage:home'))

    if request.method=='GET':
        return render(request, 'login.html')
    username = request.POST['username']
    password = request.POST['pass']
    user = authenticate(username=username, password=password)
    if user is not None and user.is_active:
        login(request, user)
        return redirect(reverse('parametrage:home'))
    else:
        return redirect(reverse('parametrage:check'))

@login_required
def uncheck(request):
    logout(request)
    return redirect(reverse('parametrage:check'))

class CandidatListView(View):
    def post(self, request, *args, **kwargs):
        pass
    
    def get(self, request, *args, **kwargs):
        context={
            "annee":annee.objects.filter(etat=True),
            "promotion":promotions.objects.filter(etat=True,type=1),
            "candidat":Candidat.objects.filter(etat=True)
        }
        return render(request, 'liste_candidat.html',context)

class CandidatsView(View):
    def post(self, request,):
        try:
            requette= Candidat.objects.get(code_candidat=request.POST.get("code"))
        except Candidat.DoesNotExist:
            requette=None
            Candidat.objects.create(
                code_candidat = request.POST.get("code"),
                nom = request.POST.get("name"),
                postnom = request.POST.get("pastname"),
                prenom = request.POST.get("Prenom"),
                sexe = request.POST.get("sexe"),
                etat_civil = request.POST.get("etatciv"),
                telephone = request.POST.get("telephone"),
                adresse = request.POST.get("adresse"),
                date_naissance = request.POST.get("datnaisse"),
                lieu_naissance = request.POST.get("lieu"),
                etat = True,
                user_id=request.user.id,
                anne_id=request.POST.get("annee")
            )
            messages.success(request, 'Candidat enregistré avec succes')
            return redirect(reverse('inscription:candidats'))
           
                
         
    
    def get(self, request, *args, **kwargs):
        context={
            "annee":annee.objects.filter(etat=True),
            "promotion":promotions.objects.filter(etat=True,type=1)
        }
        return render(request, 'candidat.html',context)
    


    
    
