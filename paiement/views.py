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
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

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
                        indice='plage'+ str(result.id)
                        tranche=float(self.request.POST.get(indice))
                        if montant == tranche:
                            result.montant=self.request.POST.get('Montant')
                            result.devise=self.request.POST.get('devise')
                            requette=Fraistranche.objects.get(fraistranche_id=result.id)
                            if requette:
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
                        pass
                        
                    
                    
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
        
        
