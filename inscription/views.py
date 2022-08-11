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
            "candidat":Testadmin.objects.filter(candidat__etat=True).values('candidat_id','candidat__nom','candidat__postnom','candidat__prenom','candidat__code__code_candi','candidat__telephone','candidat__sexe')
        }
        return render(request, 'liste_candidat.html',context)

class CandidatsView(View):
    def post(self, request,):
        if request.method == 'POST' and request.FILES :
    
                 requette = Paimentinscription.objects.get(code_candi= request.POST.get('code'),indice = "0")
                 if requette :
                     requettes=Candidat(
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
                        code_id=requette.id
                     )
                     requettes.save()
                     try:
                         resu=Testadmin.objects.get(candidat_id=requettes.id,classe_id= request.POST.get("promotion"),anne_id=request.POST.get("annee"))
                     except Testadmin.DoesNotExist:
                         Testadmin.objects.create(
                            candidat_id=requettes.id,
                            classe_id=request.POST.get("promotion"),
                            anne_id=request.POST.get("annee")
                            )
                     file_name = request.FILES.getlist('img_dossier')
                     if file_name:
                        for image in file_name:
                            new_file = Dossier(
                                candidat_id = requettes.id,
                                dossierss = image
                            )
                            new_file.save()
                     else:
                         pass
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
        if request.method =='POST':
            try:
                resu=Paimentinscription.objects.get(code_candi= request.POST.get('code'))
                if resu :
                     resu.prix_id=request.POST.get('promotion')
                     resu.code_candi =request.POST.get('code')
                     resu.observation=request.POST['Candidat']
                     resu.montant=request.POST.get('Montant')
                     resu.save()
                     valeur = 'Modification avec success '
                     messages.success(request, valeur)
                     return redirect(reverse('inscription:paiement'))
            except Paimentinscription.DoesNotExist:
                saving=Paimentinscription(
                    prix_id=request.POST.get('promotion'),
                    code_candi=request.POST.get('code'),
                    observation=request.POST.get('Candidat'),
                    montant=request.POST.get('Montant')  
                )
            saving.save()
            messages.success(request, 'paiement enregistré avec succes')
            return redirect(reverse('inscription:paiement'))
    
    def get(self,request):
       # var=annee.objects.filter(etat=True)
        s = shortuuid.ShortUUID(alphabet="0123456789")
        otp = s.random(length=5)
        context={
            "annee":annee.objects.filter(etat=True),
            "frais":Fixation.objects.filter(etat=True),
            "code":otp,
            "paiement":Paimentinscription.objects.all().values('id','prix__libelle','prix__anne__libelle','code_candi','observation','montant','created_at','prix__devise').order_by('-id')
        }

        return render(request,'paiement.html',context)

def getpaiement(request):
    if request.method == 'POST':
        resultat=Paimentinscription.objects.filter(id=request.POST.get('id')).values('id','prix__anne_id','montant','observation','prix_id','code_candi')
        return JsonResponse({'data':list(resultat)},safe=False)


    


    
    
