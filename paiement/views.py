from multiprocessing import context
from operator import concat
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from parametrage.models import annee,promotions,etudiants
from .models import *
from django.db.models.functions import Concat
from cote.models import etudprom
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Sum,Value
import shortuuid
from num2words import num2words
from datetime import date,datetime
from inscription.views import lienImage
from pyreportjasper import JasperPy
import os
from django.conf import settings
# Create your views here.
fn = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

class Paiement_fraisView(View):
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            try:
                result=Fraisclasse.objects.get(anne_id=self.request.POST.get('anee'),promotion_id=self.request.POST.get('promotion'),frais_id=self.request.POST.get('frais'))
                if result:
                    nbre=int(self.request.POST.get('nbre'))
                    if nbre == 1:
                        montant=float(self.request.POST.get('Montant'))
                        requette=Fraistranche.objects.get(fraistranche_id=result.id)
                        if requette:
                            indice='plage'+ str(requette.id)
                            if self.request.POST.get(indice) is not None:
                                tranche=float(self.request.POST.get(indice))
                                if montant == tranche:
                                    result.montant=self.request.POST.get('Montant')
                                    result.devise=self.request.POST.get('devise')
                                    requette.montant=tranche
                                    requette.devise=self.request.POST.get('devise')
                                    requette.save()
                                    result.save() 
                                    messages.success(request, 'modification avec succes')
                                    return redirect(reverse('paiement:paiement_frais'))
                            else:
                                messages.error(request, 'veuillez verifier votre repartition')
                                return redirect(reverse('paiement:paiement_frais'))
                                
                    elif nbre > 0:
                        montant=float(self.request.POST.get('Montant'))
                        requette=Fraistranche.objects.filter(fraistranche_id=result.id)
                        tranche=0
                        for ligne in requette:
                            indice ='plage'+ str(ligne.id)
                            tranche +=float(self.request.POST.get(indice))
                        if montant == tranche:
                            result.montant=self.request.POST.get('Montant')
                            result.devise=self.request.POST.get('devise')
                            result.save()
                            for ligne in requette:
                                indice='plage'+str(ligne.id)
                                ligne.montant=self.request.POST.get(indice)
                                ligne.devise=self.request.POST.get('devise')
                                ligne.save()
                                
                            messages.success(request, 'modification avec succes')
                            return redirect(reverse('paiement:paiement_frais'))
                        else:
                            messages.error(request, 'le montant de la tranche doit etre egal au montant de frais')
                            return redirect(reverse('paiement:paiement_frais'))
                                
                                    
            except Fraisclasse.DoesNotExist:
                result=None
                nbre=int(self.request.POST.get('nbre'))
                if nbre == 1:
                    if self.request.POST.get('plage1') and self.request.POST.get('plage1') is not None:
                        montant=float(self.request.POST.get('Montant'))
                        tranche=float(self.request.POST.get('plage1'))
                        if montant == tranche:
                            result=Fraisclasse(
                            anne_id=self.request.POST.get('anee'),
                            promotion_id=self.request.POST.get('promotion'),
                            frais_id=self.request.POST.get('frais'),
                            montant=self.request.POST.get('Montant'),
                            devise=self.request.POST.get('devise'))
                            result.save()
                            requette=Fraistranche(
                                tranche='1er Tranche',
                                montant=self.request.POST.get('plage1'),
                                devise=self.request.POST.get('devise'),
                                fraistranche_id=result.id   
                            )
                            requette.save()
                            messages.success(request, 'Frais Classe ajoutée')
                            return redirect(reverse('paiement:paiement_frais'))
                       
                    else:
                        messages.error(request, 'verifier bien votre repartition')
                        return redirect(reverse('paiement:paiement_frais'))
                elif nbre > 1:
                    montant=float(self.request.POST.get('Montant'))
                    tranche=0
                    nbre+=1
                    for i in range(1,nbre):
                        indice='plage'+str(i)
                        tranche +=float(self.request.POST.get(indice))
                    
                    if montant == tranche:
                        result=Fraisclasse(
                           anne_id=self.request.POST.get('anee'),
                           promotion_id=self.request.POST.get('promotion'),
                           frais_id=self.request.POST.get('frais'),
                           montant=self.request.POST.get('Montant'),
                           devise=self.request.POST.get('devise'))
                        result.save()
                        for i in range(1,nbre):
                            indice='plage' + str(i)
                            libtranche =''
                            if i== 1:
                                libtranche ='1er Tranche'
                            elif i== 2:
                                 libtranche ='2eme Tranche'
                            else:
                                libtranche ='3eme Tranche'
                                
                            requette=Fraistranche(
                            tranche=libtranche,
                            montant=self.request.POST.get(indice),
                            devise=self.request.POST.get('devise'),
                            fraistranche_id=result.id   
                            )
                            requette.save()
                            
                        messages.success(request, 'Frais Classe ajoutée')
                        return redirect(reverse('paiement:paiement_frais')) 
                    else:
                        messages.error(request, 'la repartition de tranche doit correspondre au montant de la promotion')
                        return redirect(reverse('paiement:paiement_frais'))        
    
    def get(self, request, *args, **kwargs):
        context={
            "annee":annee.objects.filter(etat=True),
            "promotion":promotions.objects.filter(etat=True),
            "frais":Frais.objects.all(),
            "Frais_classe":Fraisclasse.objects.all().values('id','anne__libelle','promotion__libelle','frais__type','devise','montant').order_by('-id'),
        }
        return render(request,"form_frais_classe.html",context)

def getfrais(request):
    result=Fraisclasse.objects.filter(pk=request.POST.get('id')).values('id','anne_id','promotion_id','frais_id','devise','montant')
    result1=Fraistranche.objects.filter(fraistranche_id=request.POST.get('id')).values('id','montant',)
    data={
        "frais_classe":list(result),
        "frais_tranche":list(result1)
    }
    return JsonResponse(data,safe=False)

def delete_frais_classe(request):
    result=Fraistranche.objects.filter(fraistranche_id=request.POST.get('id')).delete()
    resultd=Fraisclasse.objects.filter(id=request.POST.get('id')).delete()
    return JsonResponse({'status':200},safe=False)


class Paiement_templateView(View):
    def get(self, request, *args, **kwargs):
        s = shortuuid.ShortUUID(alphabet="0123456789")
        otp = s.random(length=5)
        context={
            "annee":annee.objects.filter(etat=True),
            "promotion":promotions.objects.filter(etat=True),
            "etudiant":etudprom.objects.filter(annee__etat=True).values('id','matricule_id','matricule__matricule','matricule__nom','matricule__postnom','matricule__prenom'),
            "code":otp
        }
        return render(request,'paiement_academie.html',context)
    def post(self, request, *args, **kwargs):
        totalpaye=float(self.request.POST.get('totalpaye'))
        frais=Fraistranche.objects.filter(fraistranche_id=self.request.POST.get('frais')).order_by('id')
        message=''
        if totalpaye == 0:
            if frais.count() == 1:
                rec=save_paiement(self.request)
                if rec == 1:
                    return HttpResponse("true")
            else :
               
                indice=1
                for ligne in frais:
                    if ligne.id == int(self.request.POST.get('tranche')):
                        if indice == 1 :
                            rec=save_paiement(self.request)
                            if rec == 1:
                                return HttpResponse("true")
                        else:
                            message='vous devrez finir le paiement de la tranche precedente'
                            return JsonResponse({"message":message},safe=False)
                    else :
                        indice+=1 
        else:
            if frais.count() == 1:
                rec=save_paiement(self.request)
                if rec == 1:
                    messages.success(request, 'Paiement effectué')
                    return HttpResponse("true")
            else:
                indice=1
                montant_tranche=0
                for ligne in frais:
                    montant_tranche=ligne.montant
                    if ligne.id == int(self.request.POST.get('tranche')):
                        if indice == 1 :
                            if float(self.request.POST.get('montanttranche')) > totalpaye:
                                rec=save_paiement(self.request)
                                if rec == 1:
                                    return HttpResponse("true")
                                    
                            else:
                                message='cette tranche est deja payé'
                                return JsonResponse({"message":message},safe=False)
                        else:
                            if montant_tranche == totalpaye or totalpaye > montant_tranche:
                                rec=save_paiement(self.request)
                                if rec == 1:
                                    return HttpResponse("true")
                            else:
                                message='vous devrez finir le paiement de la tranche precedente'
                                return JsonResponse({"message":message},safe=False)
                    indice+=1

def save_paiement(request):
    resultat=Paiement_frais(
        code_paie=request.POST.get('code'),
        matricule_id=request.POST.get('etudiant'),
        tranche_id=request.POST.get('tranche'),
        anne_id=request.POST.get('anee'),
        montantpaie=request.POST.get('montant'),
        user_id=request.user.id,
        frais_id=request.POST.get('new_code'),
    )
    resultat.save()
    totalpaye=float(request.POST.get('totalpaye')) + float(request.POST.get('montant'))
    reste=float(request.POST.get('montantfrais')) - float(totalpaye)
    array_data = {
        "dateOp":date.today(),
        "code_paie":request.POST.get('code'),
        "montlettre":num2words(request.POST.get('montant'),lang='fr'),
        "totalfrais": request.POST.get('montantfrais'),
        "totalreste" : reste,
        "totalpaye": totalpaye,
        "totaltranche":request.POST.get('montanttranche'),
        "montantpaie":request.POST.get('montant'),
        "frais_id":request.POST.get('new_code'),
        "user_id":request.user.id,
        "matricule_id":request.POST.get('etudiant'),
        "anne_id":request.POST.get('anee'),
        "promotion_id":request.POST.get('promotion'),
        "devise":request.POST.get('devise'),
        "tranche_id":request.POST.get('tranche'),
        }
    if imprimer_formate(array_data) == 1:
        imag=lienImage(fn)
        filename ='reçu_paiement.jrxml'
        parameters={'lien': '{}'.format(imag)}
        val=call_jasperpdf(filename,parameters)
        return val

    
def get_imprimer(request,var_id):
    code=int(var_id)
    result=Paiement_frais.objects.filter(id=code).values('tranche__fraistranche__devise','tranche__montant','frais_id','tranche__fraistranche__montant','code_paie','montantpaie','tranche__fraistranche__promotion_id','anne_id','matricule_id','created_at__date','tranche_id')
    if result.exists():
        somme=Paiement_frais.objects.filter(anne_id=result[0]["anne_id"],matricule_id=result[0]["matricule_id"],frais_id=result[0]["frais_id"]).aggregate(Sum('montantpaie')).get('montantpaie__sum')
        if somme is None:
            somme=0
        totalpaye=float(somme)
        reste=float(result[0]["tranche__fraistranche__montant"]) - float(somme)
        array_data = {
            "dateOp":result[0]["created_at__date"],
            "code_paie":result[0]["code_paie"],
            "montlettre":num2words(result[0]["montantpaie"],lang='fr'),
            "totalfrais": result[0]["tranche__fraistranche__montant"],
            "totalreste" : reste,
            "totalpaye": totalpaye,
            "totaltranche":result[0]["tranche__montant"],
            "montantpaie":result[0]["montantpaie"],
            "frais_id":result[0]["frais_id"],
            "user_id":request.user.id,
            "matricule_id":result[0]["matricule_id"],
            "anne_id":result[0]["anne_id"],
            "promotion_id":result[0]["tranche__fraistranche__promotion_id"],
            "devise":result[0]["tranche__fraistranche__devise"],
            "tranche_id":result[0]["tranche_id"],
            }
        if imprimer_formate(array_data) == 1:
            imag=lienImage(fn)
            filename ='reçu_paiement.jrxml'
            parameters={'lien': '{}'.format(imag)}
            if call_jasperpdf(filename,parameters) == 1:
                return HttpResponse("true") 
    

def imprimer_formate(con={}):
    Impression_paie.objects.all().delete()
    Impression_paie.objects.create(**con)
    return 1

def get_etudiant(request,anne,promotion):
    result=etudprom.objects.filter(annee_id=anne,promotion_id=promotion).values('id','matricule_id','matricule__matricule','matricule__nom','matricule__postnom','matricule__prenom')
    requette=Fraisclasse.objects.filter(anne_id=anne,promotion_id=promotion).values('id','frais__type','montant','devise','frais_id')
    data={
        'data':list(result),
        'frais':list(requette)}
    return JsonResponse(data,safe=False)

def get_tranche(request,anne,promotion,frais):
    resultte=Fraistranche.objects.filter(fraistranche_id=frais).values('id','tranche','montant').order_by('id')
    data={
        'data':list(resultte)}
    return JsonResponse(data,safe=False)
        
    
    
def get_montant(request):
    if request.POST.get('frais') != '':
        result_detail=Paiement_frais.objects.filter(anne_id=request.POST.get('annee'),matricule_id=request.POST.get('etudiant'),frais_id=request.POST.get('frais')).values('id','anne__libelle','matricule__nom','matricule__postnom','matricule__prenom','frais__type','tranche__tranche','montantpaie').order_by('-id')
        somme=result_detail.aggregate(Sum('montantpaie')).get('montantpaie__sum')
        if somme is None:
            somme=0  
        data={
            "totalpaye":somme,
            "data":list(Paiement_frais.objects.filter(anne_id=request.POST.get('annee'),matricule_id=request.POST.get('etudiant')).values('id','anne__libelle','matricule__nom','matricule__postnom','matricule__prenom','frais__type','tranche__tranche','montantpaie').order_by('-id'))
        }
        return JsonResponse(data,safe=False)
    else :
        data={
            "totalpaye":0,
            "data":list(Paiement_frais.objects.filter(anne_id=request.POST.get('annee'),matricule_id=request.POST.get('etudiant')).values('id','anne__libelle','matricule__nom','matricule__postnom','matricule__prenom','frais__type','tranche__tranche','montantpaie').order_by('-id'))
        }
        return JsonResponse(data,safe=False)
           
def delete_paie(request):
    result = Paiement_frais.objects.get(id=request.POST.get('id')).delete() 
    return JsonResponse({'status':200},safe=False) 

class Relevent(View):
    def get(self, request):
        context={
            "annee":annee.objects.all().order_by('-id'),
            "promotion":promotions.objects.filter(etat=True),
            "etudiant":etudiants.objects.filter(etat=True).values('id','matricule','nom','postnom','prenom'),
        }
        return render(request,'releve.html',context)
    
    def post(self, request):
        imag=lienImage(fn)
        parameters={'annee': '{}'.format(self.request.POST.get('annee')),'etudiant': '{}'.format(self.request.POST.get('etudiant')),'lien': '{}'.format(imag)}
        return HttpResponse("true") if call_jasperpdf('releves.jrxml',parameters) == 1 else HttpResponse("false")

def get_releve(request,anne,matricule):
    resultat={}
    if anne == '-1':
        resultat=Paiement_frais.objects.filter(matricule_id=matricule).values('id','anne__libelle','frais__type','tranche__tranche','tranche__fraistranche__promotion__libelle','montantpaie','tranche__devise','created_at').order_by('-id')
    else:
        resultat=Paiement_frais.objects.filter(matricule_id=matricule,anne_id=anne).values('id','anne__libelle','frais__type','tranche__tranche','tranche__fraistranche__promotion__libelle','montantpaie','tranche__devise','created_at').order_by('-id')
    
    return JsonResponse({"data":list(resultat)},safe=False)

def rapport_journalier(request):
    context={'frais':Frais.objects.all().order_by('-id')}
    return render(request,'rapport_jour.html',context)

def get_rapportJ(request,dates,datess):
    resultat=Paiement_frais.objects.filter(created_at__date__range=(dates,datess)).annotate(names=Concat('matricule__nom',Value(' '),'matricule__postnom',Value(' '),'matricule__prenom')).values('id','anne__libelle','frais__type','tranche__tranche','tranche__fraistranche__promotion__libelle','montantpaie','tranche__devise','created_at','names').order_by('-id')
    return JsonResponse({"data":list(resultat)},safe=False)

def liste_frais(request):
    imag=lienImage(fn)
    parametere={'annes': '{}'.format(request.POST.get('id_annee')),'classes': '{}'.format(request.POST.get('id_classe')),'lien': '{}'.format(imag)}
    return HttpResponse("true") if call_jasperpdf('liste_frais_classe.jrxml',parametere) == 1 else HttpResponse("false")
    
def liste_detail(request):
    imag=lienImage(fn)
    parameters={'anne': '{}'.format(int(request.POST.get('anne'))),'classe': '{}'.format(int(request.POST.get('classe'))),'lien': '{}'.format(imag)}
    return HttpResponse("true") if call_jasperpdf('detail_tranche.jrxml',parameters) == 1 else HttpResponse("false")

def print_situation(request):
    imag=lienImage(fn)
    date_du=datetime.strptime(request.POST.get('date_du'), "%Y-%m-%d").strftime("%d/%m/%Y")
    date_au=datetime.strptime(request.POST.get('date_au'), "%Y-%m-%d").strftime("%d/%m/%Y")
    parameters={'date_du': '{}'.format(date_du),'date_au': '{}'.format(date_au),'lien': '{}'.format(imag)}
    return HttpResponse("true") if call_jasperpdf('situation_paie.jrxml',parameters) == 1 else HttpResponse("false")
    
def call_jasperpdf(var_file,parameteres={}):
    input_file = os.path.join(fn, var_file)  # + "\{}".format("etatbesoin.jrxml")
    output = os.path.join(fn, 'media')  # fn + "\media"
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
        parameters=parameteres,
        locale='en_US'
    )
    return 1
    
    
    
    
    
   
        
  
        
        
    
        
    
        
      
    
        
        
