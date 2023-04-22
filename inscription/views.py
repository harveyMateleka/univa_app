from pickle import FALSE
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from .models import *
from parametrage.models import annee,promotions,etudiants,universite
from cote.models import etudprom
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
import random
import shortuuid
from django.db import transaction
import pandas as pd
from django.db.models import Count
import os
from django.conf import settings
from pyreportjasper import JasperPy
#from io import StringIO


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
        if 'importation' in self.request.POST:
            if self.request.POST.get('annee')!='-1' and self.request.POST.get('promotion')!='-1':
                df = pd.read_excel(request.FILES['excelfile'])
                with transaction.atomic():
                     for candidat in df.values.tolist():
                         resul=Paimentinscription.objects.get(code_candi=candidat[0],indice="0")
                         if resul:
                            requettes=Candidat(
                                 nom = candidat[1] if not pd.isna(candidat[1]) else None,
                                 postnom = candidat[2] if not pd.isna(candidat[2]) else None,
                                 prenom = candidat[3] if not pd.isna(candidat[3]) else None,
                                 sexe = candidat[4] if not pd.isna(candidat[4]) else None,
                                 etat_civil = candidat[5] if not pd.isna(candidat[5]) else None,
                                 telephone = candidat[6] if not pd.isna(candidat[6]) else None,
                                 adresse = candidat[7] if not pd.isna(candidat[7]) else None,
                                 date_naissance = candidat[8] if not pd.isna(candidat[8]) else None,
                                 lieu_naissance = candidat[9] if not pd.isna(candidat[9]) else None,
                                 etat = True,
                                 user_id=self.request.user.id,
                                 code_id=resul.id
                                )
                            requettes.save()
                            resul.indice='1'
                            resul.save()
                            try:
                                resu=Testadmin.objects.get(candidat_id=requettes.id,classe_id=self.request.POST.get("promotion"),anne_id=self.request.POST.get('annee'))
                            except Testadmin.DoesNotExist:
                                Testadmin.objects.create(
                                    candidat_id=requettes.id,
                                    classe_id=self.request.POST.get("promotion"),
                                    anne_id=self.request.POST.get("annee")
                                    ) 
                data={"statut":200}
                return JsonResponse(data,safe=False) 
            else :
                return  HttpResponse()
        elif 'candidat_reussie' in self.request.POST:
            if self.request.POST.get('annee')!='-1' and self.request.POST.get('promotion')!='-1':
                df = pd.read_excel(request.FILES['excelfile'])
                with transaction.atomic():
                    for candidat in df.values.tolist():
                        resul=Candidat.objects.get(code__code_candi=candidat[0],code__indice="1",etat=True)
                        if resul:
                            s = shortuuid.ShortUUID(alphabet="0123456789")
                            otp = s.random(length=5)
                            et = etudiants(
                                matricule="Mtr-"+otp,
                                nom = resul.nom,
                                postnom = resul.postnom,
                                prenom = resul.prenom,
                                sexe = resul.sexe,
                                etat_civil = resul.etat_civil,
                                telephone = resul.telephone,
                                adresse = resul.adresse,
                                date_naissance = resul.date_naissance,
                                lieu_naissance = resul.lieu_naissance,
                                user_id=self.request.user.id,
                                )
                            et.save()
                            etudprom.objects.create(
                                matricule_id=et.id,
                                promotion_id=self.request.POST.get("promotion"),
                                annee_id=self.request.POST.get("annee"),  
                            )
                            resul.reussie="1"
                            resul.save()
                return JsonResponse({'status':200},safe=False)  
                            
                
            
            
          
    
    def get(self, request, *args, **kwargs):
        context={
            "annee":annee.objects.filter(etat=True),
            "promotion":promotions.objects.filter(etat=True,type=1),
        }
        return render(request, 'liste_candidat.html',context)

class CandidatsView(View):
    def post(self, request,):
        if request.method == 'POST' and request.FILES :
    
                 requette = Paimentinscription.objects.get(code_candi= request.POST.get('code'),indice = "0")
                 if requette :
                     try:
                         requettes=Candidat.objects.get(nom=request.POST.get("name"),postnom = request.POST.get("pastname"), prenom = request.POST.get("Prenom"))
                         if requettes:
                             try:
                                resu=Testadmin.objects.get(candidat_id=requettes.id,classe_id= request.POST.get("promotion"),anne_id=request.POST.get("annee"))
                             except Testadmin.DoesNotExist:
                                Testadmin.objects.create(
                                    candidat_id=requettes.id,
                                    classe_id=request.POST.get("promotion"),
                                    anne_id=request.POST.get("annee")
                                    )
                     except Candidat.DoesNotExist:
                         requettes=None
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
                     requette.indice="1"
                     requette.save()
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
        requette=Testadmin.objects.filter(anne_id=anne,candidat__etat=True,candidat__reussie='0').values('id','candidat_id','candidat__nom','candidat__postnom','candidat__prenom','candidat__code__code_candi','candidat__telephone','candidat__sexe','candidat__reussie','anne__libelle','classe__libelle').order_by('id',)
        data={"data":list(requette)}
        return JsonResponse(data,safe=False)
    else:
        requette=Testadmin.objects.filter(anne_id=anne,classe_id=promotion,candidat__etat=True,candidat__reussie='0').values('id','candidat_id','candidat__nom','candidat__postnom','candidat__prenom','candidat__code__code_candi','candidat__telephone','candidat__sexe','candidat__reussie','anne__libelle','classe__libelle').order_by('id',)
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
        }

        return render(request,'paiement.html',context)

def getpaiement(request):
    if request.method == 'POST':
        resultat=Paimentinscription.objects.filter(id=request.POST.get('id')).values('id','prix__anne_id','montant','observation','prix_id','code_candi')
        return JsonResponse({'data':list(resultat)},safe=False)

def get_id_candidat(request,id):
    teste=Testadmin.objects.filter(pk=id).order_by('id')
    resultat=Candidat.objects.filter(id=teste[0].candidat_id).values('id','nom','postnom','prenom','sexe','telephone','email','date_naissance','lieu_naissance','etat_civil')
    dossier=Dossier.objects.filter(candidat_id=teste[0].candidat_id).order_by('id')
    context={
        'candidat':resultat,
        'parcours':teste,
        'dossier':dossier,
    }
    return render(request, 'candidat_detail.html',context)

def edit_etudiant(request):
    if request.method == 'POST':
        result_test=Testadmin.objects.get(pk=request.POST.get('id'))
        if result_test:
            result=Candidat.objects.get(pk=result_test.candidat_id,etat=True)
            if result:
                s = shortuuid.ShortUUID(alphabet="0123456789")
                otp = s.random(length=5)
                et = etudiants(
                    matricule="Mtr-"+otp,
                    nom = result.nom,
                    postnom = result.postnom,
                    prenom = result.prenom,
                    sexe = result.sexe,
                    etat_civil = result.etat_civil,
                    telephone = result.telephone,
                    adresse = result.adresse,
                    date_naissance = result.date_naissance,
                    lieu_naissance = result.lieu_naissance,
                    user_id=request.user.id,
                    )
                et.save()
                etudprom.objects.create(
                    matricule_id=et.id,
                    promotion_id=result_test.classe_id,
                    annee_id=result_test.anne_id,  
                )
                result.reussie="1"
                result.save()
                return JsonResponse({'status':200},safe=False) 

def desapprov(request):
    resultat=Testadmin.objects.get(id=request.POST.get('id'))
    if resultat:
        resul=Candidat.objects.get(id=resultat.candidat_id)
        if resul:
            if resul.etat == True:
                resul.etat=False
            else:
                resul.etat=True
            resul.save()
            return JsonResponse({'status':200},safe=False)
        
def getpaiement_all(request):
     return JsonResponse({'data':list(Paimentinscription.objects.all().values('id','prix__libelle','prix__anne__libelle','code_candi','observation','montant','created_at','prix__devise').order_by('-id'))},safe=False)

def get_candidat_inactif(request):
    requette=Testadmin.objects.filter(candidat__etat=False,candidat__reussie='0').values('id','candidat_id','candidat__nom','candidat__postnom','candidat__prenom','candidat__code__code_candi','candidat__telephone','candidat__sexe','candidat__reussie','anne__libelle','classe__libelle').order_by('id',)
    data={"data":list(requette)}
    return JsonResponse(data,safe=False)

def index_inactif(request):
    return render(request, 'liste_candidat_inactif.html')

def statistique_C(request):
    return render(request, 'statistique_candidat.html',{'annee':annee.objects.all().order_by("-id")})

def destroy_paie(request):
    result=Paimentinscription.objects.get(pk=request.POST.get('id'))
    result.delete()
    return JsonResponse({'status':200},safe=False) 

def statique_candidat(request,anne,valeur):
    resultat={}
    if valeur == '1':
        resultat=Testadmin.objects.filter(anne_id=anne,candidat__reussie="1").values('classe__libelle').order_by('classe_id').annotate(nbre=Count('candidat_id'))
    else:
        resultat=Testadmin.objects.filter(anne_id=anne).values('classe__libelle').order_by('classe_id').annotate(nbre=Count('candidat_id'))
    return JsonResponse({'data':list(resultat)},safe=False)

def statistique_promo_montant(request):
    context={} 

def imprime_statistique(request):
    
    fn = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(fn, 'statistique_C.jrxml')  # + "\{}".format("etatbesoin.jrxml")
    output = os.path.join(fn, 'media')  # fn + "\media"
    imag=lienImage(fn)
    con = {
        'driver': 'generic',
        'jdbc_driver': 'org.postgresql.Driver',
        'jdbc_url': f"jdbc:postgresql://localhost:{settings.DATABASES['default']['PORT']}/"+str(settings.DATABASES['default']['NAME']),
        'jdbc_dir': fn,
        'username': settings.DATABASES['default']['USER'],
        'password': settings.DATABASES['default']['PASSWORD']
    }
    jasper = JasperPy()
            # jasper.compile("D:/test1.jrxml")
            # jasper.path_executable = "D:/JasperStarter/bin/"
    jasper.process(
        input_file,
        output,
        format_list=["pdf"],
        db_connection=con,
        parameters={'var_anne': '{}'.format(request.POST.get('anne')),'lien': '{}'.format(imag)},
        locale='en_US'
    )

    return HttpResponse("true")

def imprime_statistique_r(request):
    
    fn = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(fn, 'statistique_R.jrxml')  # + "\{}".format("etatbesoin.jrxml")
    output = os.path.join(fn, 'media')  # fn + "\media"
    imag=lienImage(fn)
    con = {
        'driver': 'generic',
        'jdbc_driver': 'org.postgresql.Driver',
        'jdbc_url': f"jdbc:postgresql://localhost:{settings.DATABASES['default']['PORT']}/"+str(settings.DATABASES['default']['NAME']),
        'jdbc_dir': fn,
        'username': settings.DATABASES['default']['USER'],
        'password': settings.DATABASES['default']['PASSWORD']
    }
    jasper = JasperPy()
            # jasper.compile("D:/test1.jrxml")
            # jasper.path_executable = "D:/JasperStarter/bin/"
    jasper.process(
        input_file,
        output,
        format_list=["pdf"],
        db_connection=con,
        parameters={'var_anne': '{}'.format(request.POST.get('anne')),'lien': '{}'.format(imag),'reussie':'{}'.format(request.POST.get('reussie'))},
        locale='en_US'
    )

    return HttpResponse("true")

def imprime_inactif(request):
    fn = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(fn, 'candidat_inactif.jrxml')  # + "\{}".format("etatbesoin.jrxml")
    output = os.path.join(fn, 'media')  # fn + "\media"
    imag=lienImage(fn)
    con = {
        'driver': 'generic',
        'jdbc_driver': 'org.postgresql.Driver',
        'jdbc_url': f"jdbc:postgresql://localhost:{settings.DATABASES['default']['PORT']}/"+str(settings.DATABASES['default']['NAME']),
        'jdbc_dir': fn,
        'username': settings.DATABASES['default']['USER'],
        'password': settings.DATABASES['default']['PASSWORD']
    }
    val=False
    jasper = JasperPy()
            # jasper.compile("D:/test1.jrxml")
            # jasper.path_executable = "D:/JasperStarter/bin/"
    jasper.process(
        input_file,
        output,
        format_list=["pdf"],
        db_connection=con,
        parameters={'etat': '{}'.format(val),'lien': '{}'.format(imag)},
        locale='en_US'
    )

    return HttpResponse("true")
    

def lienImage(lien):
    u=universite.objects.all()
    if u:
        u=u.first().upload.url
        return f'{lien}{u}'
    else:
        return f'{lien}/media/logo_images/logodefo.png'

def liste_candidat(request):
    fn = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(fn, 'liste_candidat.jrxml')  # + "\{}".format("etatbesoin.jrxml")
    output = os.path.join(fn, 'media')  # fn + "\media"
    imag=lienImage(fn)
    con = {
        'driver': 'generic',
        'jdbc_driver': 'org.postgresql.Driver',
        'jdbc_url': f"jdbc:postgresql://localhost:{settings.DATABASES['default']['PORT']}/"+str(settings.DATABASES['default']['NAME']),
        'jdbc_dir': fn,
        'username': settings.DATABASES['default']['USER'],
        'password': settings.DATABASES['default']['PASSWORD']
    }
   
    jasper = JasperPy()
            # jasper.compile("D:/test1.jrxml")
            # jasper.path_executable = "D:/JasperStarter/bin/"
    jasper.process(
        input_file,
        output,
        format_list=["pdf"],
        db_connection=con,
        parameters={'annee': '{}'.format(request.POST.get('anne')),'classe': '{}'.format(request.POST.get('classe')),'lien': '{}'.format(imag)},
        locale='en_US'
    )

    return HttpResponse("true")
    

       
            
            
        
    



    


    
    
