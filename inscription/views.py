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
import random
import shortuuid

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
            "candidat":Testadmin.objects.filter(candidat__etat=True).values('candidat_id','candidat__nom','candidat__postnom','candidat__prenom','candidat__code_candidat','candidat__telephone','candidat__sexe')
        }
        return render(request, 'liste_candidat.html',context)

class CandidatsView(View):
    def post(self, request,):
        if request.method == 'POST' and request.FILES :
             try:
                 requette= Candidat.objects.get(code_candidat=request.POST.get("code"))
                 if requette :
                      Testadmin.objects.create(
                        candidat_id=requette.id,
                        classe_id=request.POST.get("promotion"),
                        anne_id=request.POST.get("annee")
                    )
             except Candidat.DoesNotExist:

                 requette=None
                 requette=Candidat.objects.create(
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
                 )
                 requette.save()
                 requette = Candidat.objects.get(code_candidat=request.POST.get("code"))
                 resu=Testadmin.objects.get(candidat_id=requette.id,classe_id= request.POST.get("promotion"),anne_id=request.POST.get("annee"))
                 if resu is None:
                       Testadmin.objects.create(
                           candidat_id=requette.id,
                           classe_id=request.POST.get("promotion"),
                           anne_id=request.POST.get("annee")
                        )
                 file_name = request.FILES.getlist('img_dossier')
                 if file_name:
                     for image in file_name:
                         new_file = Dossier(
                             candidat_id = requette.id,
                             dossierss = image
                         )
                         new_file.save()
                 else:
                     print(file_name)
                 messages.success(request, 'Candidat enregistré avec succes')
                 return redirect(reverse('inscription:candidats'))
            
       
           
                
         
    
    def get(self, request, *args, **kwargs):
        context={
            "annee":annee.objects.filter(etat=True),
            "promotion":promotions.objects.filter(etat=True,type=1)
        }
        return render(request, 'candidat.html',context)

def get_candidat(request,anne,promotion):
    if promotion == '-1':
        requette=Testadmin.objects.filter(anne_id=anne).values('candidat_id','candidat__nom','candidat__postnom','candidat__prenom','candidat__code_candidat','candidat__telephone','candidat__sexe')
        data={"data":list(requette)}
        return JsonResponse(data,safe=False)
    else:
        requette=Testadmin.objects.filter(anne_id=anne,classe_id=promotion).values('candidat_id','candidat__nom','candidat__postnom','candidat__prenom','candidat__code_candidat','candidat__telephone','candidat__sexe')
        data={"data":list(requette)}
        return JsonResponse(data,safe=False)

class Paiement(View):
    def post(self,request,):
        pass
    
    def get(self,request):
       # var=annee.objects.filter(etat=True)
        s = shortuuid.ShortUUID(alphabet="0123456789")
        otp = s.random(length=5)
        context={
            "annee":annee.objects.filter(etat=True),
            "frais":Fixation.objects.filter(etat=True),
            "code":otp
        }

        return render(request,'paiement.html',context)


    


    
    
