from multiprocessing import context
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from parametrage.models import annee,promotions,etudiants
from .models import *
from cote.models import etudprom
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Sum
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
                                messages.error(request, 'le montant de la tranche doit etre egal au montant de frais')
                                return redirect(reverse('paiement:paiement_frais'))
                    elif nbre > 0:
                        montant=float(self.request.POST.get('Montant'))
                        requette=Fraistranche.objects.filter(fraistranche_id=result.id)
                        tranche=0
                        for ligne in requette:
                            indice='plage'+str(ligne.id)
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
                        messages.error(request, 'le montant de la tranche doit etre egal au montant de frais')
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

def delete_frais(request):
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
                    messages.success(request, 'Paiement effectué')
                    return redirect(reverse('paiement:get_paiements'))
            else :
               
                indice=1
                for ligne in frais:
                    if ligne.id == int(self.request.POST.get('tranche')):
                        if indice == 1 :
                            rec=save_paiement(self.request)
                        if rec == 1:
                            messages.success(request, 'Paiement effectué')
                            return redirect(reverse('paiement:get_paiements'))
                        else:
                            message='vous devrez finir le paiement de la tranche precedente'
                            messages.error(request, message)
                            return redirect(reverse('paiement:get_paiements'))  
                    else :
                        indice+=1 
        else:
            if frais.count() == 1:
                rec=save_paiement(self.request)
                if rec == 1:
                    messages.success(request, 'Paiement effectué')
                    return redirect(reverse('paiement:get_paiements'))
            else:
                indice=1
                montant_tranche=0
                for ligne in frais:
                    montant_tranche+=ligne.montant
                    if ligne.id == int(self.request.POST.get('tranche')):
                        if indice == 1 :
                            if float(self.request.POST.get('montanttranche')) > totalpaye:
                                rec=save_paiement(self.request)
                                if rec == 1:
                                    messages.success(request, 'Paiement effectué')
                                    return redirect(reverse('paiement:get_paiements'))
                                    
                            else:
                                messages.error(request, 'cette tranche est deja payé')
                                return redirect(reverse('paiement:get_paiements'))
                        else:
                            if montant_tranche == totalpaye or totalpaye > montant_tranche:
                                rec=save_paiement(self.request)
                                if rec == 1:
                                    messages.success(request, 'Paiement effectué')
                                    return redirect(reverse('paiement:get_paiements'))
                            else:
                                messages.error(request, 'ce paiement est annulé car vous devrez acquitter la tranche precedente')
                                return redirect(reverse('paiement:get_paiements'))
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
    result_detail=Paiement_frais.objects.filter(anne_id=request.POST.get('annee'),matricule_id=request.POST.get('etudiant'),frais_id=request.POST.get('frais')).values('id','anne__libelle','matricule__nom','matricule__postnom','matricule__prenom','frais__type','tranche__tranche','montantpaie').order_by('-id')
   
    somme=result_detail.aggregate(Sum('montantpaie')).get('montantpaie__sum')
    if somme is None:
        somme=0
        
    print(somme)
    data={
        "totalpaye":somme,
        "data":list(result_detail)
    }
    return JsonResponse(data,safe=False)   
def delete_paie(request):
    result = Paiement_frais.objects.filter(id=request.POST.get('id')).delete() 
    return JsonResponse({'status':200},safe=False) 
    
        
    
        
      
    
        
        
