from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from .models import *
from parametrage.models import annee,promotions

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
        data_anne=annee.objects.filter(etat=True)
        context={
            "annee":annee.objects.filter(etat=True),
            "promotion":promotions.objects.filter(etat=True,type=1)
        }
        return render(request, 'liste_candidat.html',context)
    
    
