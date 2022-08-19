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
                result=Fraisclasse.objects.get(anne_id=self.request.POST.get('annee'),promotion_id=self.request.POST.get('promotion'),frais_id=self.request.POST.get('frais'))
                if result:
                    result.montant=self.request.POST.get('montant')
                    result.devise=self.request.POST.get('devise')
                    result.save()
                    messages.success(request, 'modification avec succes')
                    return redirect(reverse('paiement:paiement_frais'))
                    
                    
            except Fraisclasse.DoesNotExist:
                result=None
                nbre=self.request.POST.get('nbre')
                if nbre == 1:
                    montant=float(self.request.POST.get('montant'))
                    tranche=float(self.request.POST.get('plage1'))
                    if montant == tranche:
                        pass
                    else:
                       messages.success(request, 'modification avec succes')
                       return redirect(reverse('paiement:paiement_frais'))
                        
                result=Fraisclasse(
                    anne_id=self.request.POST.get('annee'),
                    promotion_id=self.request.POST.get('promotion'),
                    frais_id=self.request.POST.get('frais'),
                    montant=self.request.POST.get('montant'),
                    devise=self.request.POST.get('devise'))
                result.save()
                
            
                    
                    
                    
                messages.success(request, 'operation enregistré avec succes')
                return redirect(reverse('paiement:paiement_frais'))
                
    
    def get(self, request, *args, **kwargs):
        context={
            "annee":annee.objects.filter(etat=True),
            "promotion":promotions.objects.filter(etat=True),
            "frais":Frais.objects.all()
        }
        return render(request,"form_frais_classe.html",context)
