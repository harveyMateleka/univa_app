import datetime
import os.path

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.db import transaction
from django.db.models import Count
from django.forms import DateInput
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
# from pyreportjasper import JasperPy
from cote.models import etudprom
from .models import *


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


class EtudiantsBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
    model = etudiants
    fields = '__all__'
    raise_exception = True
    success_url = reverse_lazy('parametrage:etudiants')

    def _formatcss(self, fr, f):
        fr.fields[f].widget.attrs["class"] = "form-control"
    def _formatcssnonrequired(self, fr, f):

        for x in fr.fields:
            if x not in f:
                fr.fields[x].widget.attrs["required"] = "true"
    def _formatcssdate(self, fr, f):
        for x in f:
            fr.fields[x].widget = DateInput(
                format=('%Y-%m-%d'), attrs={
                    'type': 'date',
                    'class': "form-control"
                })
    def get_form(self, *args, **kwargs):
        form = super(EtudiantsBaseView, self).get_form(*args, **kwargs)
        [self._formatcss(form, f) for f in form.fields]
        self._formatcssdate(form, ["date_naissance"])
        # self._formatcssnonrequired(form, ["observation"])
        return form
    def get_success_url(self):
        if '_continue' in self.request.POST:
            url = reverse_lazy('parametrage:etudiants_update', kwargs={'pk': self.object.pk}, )
        elif '_addanother' in self.request.POST:
            url = reverse_lazy('parametrage:etudiants_create')
        else:
            url = reverse_lazy('parametrage:etudiants')
        return url
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["annee"] = annee.objects.filter(etat=True)
        context["departement"] = departements.objects.filter(etat=True)

        return context

class EtudiantsListView(EtudiantsBaseView, ListView):
    def get(self, request, *args, **kwargs):
        if 'annee' in self.request.GET:
            if request.GET.get('promotion')=='':
                return JsonResponse({'data': []}, safe=False)
            data = etudprom.objects.filter(
                promotion_id=request.GET.get('promotion'),
                matricule__etat=True,
                                           annee_id=request.GET.get('annee')
                                           ).values(

                'matricule_id',
                'matricule__matricule',
                'matricule__nom',
                'matricule__postnom',
                'matricule__prenom',
                'matricule__sexe',
                'matricule__telephone'
            )
            data = list(data)
            return JsonResponse({'data': data}, safe=False)
        if 'departement' in self.request.GET:
            data = sections.objects.filter(etat=True,departement_id=request.GET.get('departement')
                                           ).values(

                'id',
                'libelle'
            )
            data = list(data)
            return JsonResponse({'data': data}, safe=False)
        if 'section' in self.request.GET:
            data = options.objects.filter(etat=True,section_id=request.GET.get('section')
                                           ).values(

                'id',
                'libelle'
            )
            data = list(data)
            return JsonResponse({'data': data}, safe=False)
        if 'option' in self.request.GET:
            data = promotions.objects.filter(etat=True,option_id=request.GET.get('option')
                                           ).values(

                'id',
                'libelle'
            )
            data = list(data)
            return JsonResponse({'data': data}, safe=False)
        if 'exportation' in self.request.GET:
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="etudiants.xls"'
            import xlwt
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet(str(self.request.GET.get('libpromotion')))

            row_num = 0

            font_style = xlwt.XFStyle()
            font_style.font.bold = True
            date_format = xlwt.XFStyle()
            date_format.num_format_str = 'dd/mm/yyyy'

            columns = ['Matricule', 'nom', 'Postnom', 'Prénom', 'Sexe', 'Etat civil', 'Date naissance',
                       'Lieu naissance', 'téléphone', 'Email', 'Adresse',
                       'Année academique', 'Promotion']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)  # at 0 row 0 column

            # Sheet body, remaining rows
            font_style = xlwt.XFStyle()
            rows = etudprom.objects.filter(matricule__etat=True,annee_id=self.request.GET.get('codannee'),promotion_id=self.request.GET.get('codpromotion')).\
                values_list('matricule__matricule',
                                                               'matricule__nom', 'matricule__postnom',
                                                               'matricule__prenom', 'matricule__sexe',
                                                               'matricule__etat_civil', 'matricule__date_naissance',
                                                               'matricule__lieu_naissance', 'matricule__telephone',
                                                               'matricule__email','matricule__adresse',
                                                               'annee__libelle', 'promotion__libelle')

            for row in rows:
                row_num += 1
                for col_num in range(len(row)):
                    if isinstance(row[col_num], datetime.date):
                        ws.write(row_num, col_num, row[col_num], date_format)
                    else:
                        ws.write(row_num, col_num, row[col_num], font_style)

            wb.save(response)
            return response

        return super(EtudiantsListView, self).get(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        if 'importation' in self.request.POST:
            import pandas as pd
            df = pd.read_excel(request.FILES['excelfile'])
            with transaction.atomic():
                for etudiant in df.values.tolist():

                    e = etudiants.objects.filter(matricule=etudiant[0])
                    if e:
                        pass
                    else:
                        et = etudiants.objects.create(
                            matricule=etudiant[0] if not pd.isna(etudiant[0]) else None,
                            nom=etudiant[1] if not pd.isna(etudiant[1]) else None,
                            postnom=etudiant[2] if not pd.isna(etudiant[2]) else None,
                            prenom=etudiant[3] if not pd.isna(etudiant[3]) else None,
                            sexe=etudiant[4] if not pd.isna(etudiant[4]) else None,
                            etat_civil=etudiant[5] if not pd.isna(etudiant[5]) else None,
                            date_naissance=etudiant[6] if not pd.isna(etudiant[6]) else None,
                            lieu_naissance=etudiant[7] if not pd.isna(etudiant[7]) else None,
                            telephone=etudiant[8] if not pd.isna(etudiant[8]) else None,
                            email=etudiant[9] if not pd.isna(etudiant[9]) else None,
                            user=self.request.user,
                            adresse=etudiant[10] if not pd.isna(etudiant[10]) else None
                        )
                        etudprom.objects.create(
                            matricule=et,
                            promotion_id=self.request.POST.get('codpromotion'),
                            annee_id=self.request.POST.get('codannee'))

            return HttpResponse()





class EtudiantsDetailView(EtudiantsBaseView, DetailView):

    def get_context_data(self, **kwargs):
        context = super(EtudiantsBaseView, self).get_context_data(**kwargs)
        context['parcours'] = etudprom.objects.filter(matricule_id=self.kwargs['pk']).order_by('id')
        return context

class EtudiantsCreateView(EtudiantsBaseView, CreateView):
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object = form.save()
        etudprom.objects.create(
            matricule_id=self.object.id,
            promotion_id=self.request.POST.get("promotion"),
            annee_id=self.request.POST.get("annee"))
        return super().form_valid(form)
class EtudiantsUpdateView(EtudiantsBaseView, UpdateView):

    # def form_valid(self, form):
    #     self.object = form.save(commit=False)
    #     self.object.user = self.request.user
    #     self.object = form.save()
    #     etudprom.objects.create(
    #         matricule_id=self.object.id,
    #         promotion_id=self.request.POST.get("promotion"),
    #         annee_id=self.request.POST.get("annee"))
    #     return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(EtudiantsBaseView, self).get_context_data(**kwargs)
        # data = etudprom.objects.filter(matricule_id=self.kwargs['pk']).order_by('-id').first()
        # context['promotionid'] = data.promotion.id
        # context['anneeid'] = data.annee.id
        context['update'] = 1

        return context
class EtudiantsDeleteView(EtudiantsBaseView, DeleteView):
    def get(self, request, *args, **kwargs):
        dataetudiant = etudiants.objects.get(id=self.kwargs['pk'])
        dataetudiant.etat = False
        dataetudiant.save()
        return redirect('parametrage:etudiants')
    # def form_valid(self, form):
    #     self.object = form.save(commit=False)
    #     self.object.user = self.request.user
    #     self.object = form.save()
    #     return super().form_valid(form)





#
# @login_required
# def exportetudiants(request):
#     import xlwt
#
#     lisp = {}
#     response = HttpResponse(content_type='application/ms-excel')
#     response['Content-Disposition'] = 'attachment; filename="etudiants_2022_AP1.xls"'
#
#     wb = xlwt.Workbook(encoding='utf-8')
#     ws = wb.add_sheet(annee)
#
#     row_num = 0
#
#     font_style = xlwt.XFStyle()
#     font_style.font.bold = True
#     date_format = xlwt.XFStyle()
#     date_format.num_format_str = 'dd/mm/yyyy'
#
#     columns = ['Matricule', 'Nom', 'Postnom', 'Prenom', 'Sexe', 'Telephone', 'Date Naissance', 'Lieu Naissance']
#
#     for col_num in range(len(columns)):
#         ws.write(row_num, col_num, columns[col_num], font_style)
#
#     font_style = xlwt.XFStyle()
#
#     etud=etudiants.objects.filter(etudprom__annee_id=request.POST.get('annee'),etudprom__promotion_id=request.POST.get('promotion'))
#     for i in etud:
#         row_num += 1
#         ws.write(row_num, 0, i.matricule, font_style)
#         ws.write(row_num, 1, i.nom, font_style)
#         ws.write(row_num, 2, i.postnom, font_style)
#         ws.write(row_num, 3, i.prenom, font_style)
#         ws.write(row_num, 4, i.sexe, font_style)
#         ws.write(row_num, 5, i.telephone, font_style)
#         ws.write(row_num, 6, i.datenaiss, font_style)
#         ws.write(row_num, 6, i.lieunaiss, font_style)
#     wb.save(response)
#     return response
#
#
# @login_required
# def importetudiants(request):
#     import pandas as pd
#     df = pd.read_excel(request.FILES['excelfile'])
#     for etudiant in df.values.tolist():
#         pass
#     #message
#     return redirect('parametrage:etudiants')
#
#
#     lisp = {}
#     response = HttpResponse(content_type='application/ms-excel')
#     response['Content-Disposition'] = 'attachment; filename="etudiants_2022_AP1.xls"'
#
#     wb = xlwt.Workbook(encoding='utf-8')
#     ws = wb.add_sheet(annee)
#
#     row_num = 0
#
#     font_style = xlwt.XFStyle()
#     font_style.font.bold = True
#     date_format = xlwt.XFStyle()
#     date_format.num_format_str = 'dd/mm/yyyy'
#
#     columns = ['Matricule', 'Nom', 'Postnom', 'Prenom', 'Sexe', 'Telephone', 'Date Naissance', 'Lieu Naissance']
#
#     for col_num in range(len(columns)):
#         ws.write(row_num, col_num, columns[col_num], font_style)
#
#     font_style = xlwt.XFStyle()
#
#     etud = etudiants.objects.filter(etudprom__annee_id=request.POST.get('annee'),
#                                     etudprom__promotion_id=request.POST.get('promotion'))
#     for i in etud:
#         row_num += 1
#         ws.write(row_num, 0, i.matricule, font_style)
#         ws.write(row_num, 1, i.nom, font_style)
#         ws.write(row_num, 2, i.postnom, font_style)
#         ws.write(row_num, 3, i.prenom, font_style)
#         ws.write(row_num, 4, i.sexe, font_style)
#         ws.write(row_num, 5, i.telephone, font_style)
#         ws.write(row_num, 6, i.datenaiss, font_style)
#         ws.write(row_num, 6, i.lieunaiss, font_style)
#     wb.save(response)
#     return response

# def update_psw(request):
#     if request.method == 'POST':
#         if request.user.is_authenticated:
#             if request.POST.get("nvpass") == request.POST.get("cfpass"):
#                 userdata = Utilisat.objects.get(id=request.user.id)
#                 userdata.password = make_password(request.POST.get("nvpass"))
#                 userdata.save()
#                 logout(request)
#                 return JsonResponse({'id': "1", "msg": "Opération effectuée"}, safe=False)
#                 # return redirect(reverse('parametrage:check'))
#         return JsonResponse({'id': "0", "msg": "Opération non effectuée"}, safe=False)
#
#     return render(request, 'update_password.html')
#
# def update_profile(request):
#     if request.method == 'POST':
#         if request.user.is_authenticated:
#             if request.POST.get("password")=='':
#                 userdata = Utilisat.objects.get(id=request.user.id)
#                 userdata.username = request.POST.get("username")
#                 userdata.last_name = request.POST.get("nom")
#                 userdata.first_name = request.POST.get("prenom")
#                 userdata.email = request.POST.get("email")
#                 userdata.sexe = request.POST.get("sexe")
#                 userdata.save()
#                 logout(request)
#                 return JsonResponse({'id': "1", "msg": "Opération effectuée"}, safe=False)
#                 # return redirect(reverse('parametrage:check'))
#
#             elif request.POST.get("password") == request.POST.get("cfpassword"):
#                 userdata = Utilisat.objects.get(id=request.user.id)
#                 userdata.username = request.POST.get("username")
#                 userdata.last_name = request.POST.get("nom")
#                 userdata.first_name = request.POST.get("prenom")
#                 userdata.email = request.POST.get("email")
#                 userdata.sexe = request.POST.get("sexe")
#                 userdata.password = make_password(request.POST.get("password"))
#                 userdata.save()
#                 logout(request)
#                 return JsonResponse({'id': "1", "msg": "Opération effectuée"}, safe=False)
#                 # return redirect(reverse('parametrage:check'))
#
#         return JsonResponse({'id': "0", "msg": "Opération non effectuée"}, safe=False)
#
#     return render(request, 'update_profile.html')
# class TemplateMainBord(LoginRequiredMixin,PermissionRequiredMixin,TemplateView):
#     def get_context_data(self, **kwargs):
#         context = super(TemplateMainBord, self).get_context_data(**kwargs)
#         context['etudiant'] = Etudiant.objects.filter(valide=True).exclude(isdeleted=True).count()
#         context['prof'] = Agent.objects.exclude(isdeleted=True).count()
#         context['cours'] = Cours.objects.exclude(isdeleted=True).count()
#         context['faculte'] = Faculter.objects.exclude(isdeleted=True).count()
#         context['departement'] = Departement.objects.count()
#         context['promotion'] = Promotion.objects.exclude(isdeleted=True).count()
#         context['filiere'] = Filiere.objects.exclude(isdeleted=True).count()
#         return context



# class FaculterBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Faculter
#     fields = '__all__'
#     success_url = reverse_lazy('parametrage:faculte')
#
#     # def get_queryset(self):
#     #     queryset = Faculter.objects.order_by('-id')
#     #     return queryset
#
#     def get_form(self, *args, **kwargs):
#         form = super(FaculterBaseView, self).get_form(*args, **kwargs)
#         form.fields["libelle"].widget.attrs["class"] = "form-control"
#         form.fields["libelle"].widget.attrs["placeholder"] = "Nom faculte"
#         form.fields["etablissementid"].widget.attrs["class"] = "form-control show-tick select"
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:faculte_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:faculte_create')
#         else:
#             url = reverse_lazy('parametrage:faculte')
#         return url
# class FaculterListView(FaculterBaseView, ListView):
#     pass
# class FaculterDetailView(FaculterBaseView, DetailView):
#     pass
# class FaculterCreateView(FaculterBaseView, CreateView):
#     pass
# class FaculterUpdateView(FaculterBaseView, UpdateView):
#     pass
# class FaculterDeleteView(FaculterBaseView, DeleteView):
#     pass
# @login_required
# @permission_required('parametrage.view_faculte')
# def faculte_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'faculte.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
# # class FiliereBaseView(View):
# #     model = Filiere
# #     fields = '__all__'
# #     success_url = reverse_lazy('parametrage:filiere')
# #
# #     def get_form(self, *args, **kwargs):
# #         form = super(FaculterBaseView, self).get_form(*args, **kwargs)
# #         form.fields["libelle"].widget.attrs["class"] = "form-control"
# #         form.fields["libelle"].widget.attrs["placeholder"] = "Nom faculte"
# #         form.fields["etablissementid"].widget.attrs["class"] = "form-control show-tick select"
# #         return form
# #
# #     def get_success_url(self):
# #         if '_continue' in self.request.POST:
# #             url = reverse_lazy('parametrage:faculte_update', kwargs={'pk': self.object.pk}, )
# #         elif '_addanother' in self.request.POST:
# #             url = reverse_lazy('parametrage:faculte_create')
# #         else:
# #             url = reverse_lazy('parametrage:faculte')
# #         return url
# # class FiliereListView(FiliereBaseView, ListView):
# #     pass
# # class FiliereDetailView(FiliereBaseView, DetailView):
# #     pass
# # class FiliereCreateView(FiliereBaseView, CreateView):
# #     pass
# # class FiliereUpdateView(FiliereBaseView, UpdateView):
# #     pass
# # class FiliereDeleteView(FiliereBaseView, DeleteView):
# #     pass
# # @login_required
# # @permission_required('parametrage.view_filiere')
# # def filiere_rapport(request):
# #     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# #     input_file=os.path.join(fn,'filiere.jrxml')
# #     output_file=os.path.join(fn,'media')
# #
# #     con={
# #         'driver':'generic',
# #         'jdbc_driver':'org.postgresql.Driver',
# #         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
# #         'jdbc_dir':fn,
# #         'username':settings.DATABASES['default']['USER'],
# #         'password':settings.DATABASES['default']['PASSWORD'],
# #
# #     }
# #     jasper=JasperPy()
# #     jasper.process(
# #         input_file,
# #         output_file,
# #         format_list=["pdf"],
# #         db_connection=con,
# #         #parameters={},
# #         locale='en_US'
# #     )
# #     return HttpResponse('true')
# #
#
#
# class DepartementBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Departement
#     fields = '__all__'
#     success_url = reverse_lazy('parametrage:departement')
#     def _formatcss(self,fr,f):
#         fr.fields[f].widget.attrs["class"] = "form-control"
#
#     def _formatcssnonrequired(self,fr,f):
#
#         for x in fr.fields:
#             if x not in f:
#                 fr.fields[x].widget.attrs["required"] = "true"
#
#     def _formatcssdate(self,fr,f):
#         for x in f:
#             fr.fields[x].widget = DateInput(
#             format=('%Y-%m-%d'), attrs={
#                 'type': 'date',
#                     'class':"form-control"
#             })
#
#     def get_form(self, *args, **kwargs):
#         form = super(DepartementBaseView, self).get_form(*args, **kwargs)
#         # form.fields['etablissement'].queryset=Etablissement.objects.all().order_by('nom')
#
#         [self._formatcss(form,f) for f in form.fields]
#         self._formatcssnonrequired(form, [])
#
#         form.fields['faculteid'].widget.attrs["class"] = "form-control select"
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:departement_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:departement_create')
#         else:
#             url = reverse_lazy('parametrage:departement')
#         return url
#
#
# class DepartementListView(DepartementBaseView, ListView):
#     """View to list all Departements.
#     Use the 'departement_list' variable in the template
#     to access all Departement objects"""
# class DepartementDetailView(DepartementBaseView, DetailView):
#     """View to list the details from one Departement.
#     Use the 'Departement' variable in the template to access
#     the specific Departement here and in the Views below"""
# class DepartementCreateView(DepartementBaseView, CreateView):
#     """View to create a new Departement"""
# class DepartementUpdateView(DepartementBaseView, UpdateView):
#     """View to update a Departement"""
# class DepartementDeleteView(DepartementBaseView, DeleteView):
#     """View to delete a Departement"""
#
# @login_required
# @permission_required('parametrage.view_departement')
# def departement_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'departement.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
# class CycleBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Cycle
#     fields = '__all__'
#     success_url = reverse_lazy('parametrage:cycle')
#     def _formatcss(self,fr,f):
#         fr.fields[f].widget.attrs["class"] = "form-control"
#
#     def _formatcssnonrequired(self,fr,f):
#
#         for x in fr.fields:
#             if x not in f:
#                 fr.fields[x].widget.attrs["required"] = "true"
#
#     def _formatcssdate(self,fr,f):
#         for x in f:
#             fr.fields[x].widget = DateInput(
#             format=('%Y-%m-%d'), attrs={
#                 'type': 'date',
#                     'class':"form-control"
#             })
#
#     def get_form(self, *args, **kwargs):
#         form = super(CycleBaseView, self).get_form(*args, **kwargs)
#         # form.fields['etablissement'].queryset=Etablissement.objects.all().order_by('nom')
#
#         [self._formatcss(form,f) for f in form.fields]
#         self._formatcssnonrequired(form, [])
#
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:cycle_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:cycle_create')
#         else:
#             url = reverse_lazy('parametrage:cycle')
#         return url
#
#
# class CycleListView(CycleBaseView, ListView):
#     """View to list all Departements.
#     Use the 'departement_list' variable in the template
#     to access all Departement objects"""
# class CycleDetailView(CycleBaseView, DetailView):
#     """View to list the details from one Departement.
#     Use the 'Departement' variable in the template to access
#     the specific Departement here and in the Views below"""
# class CycleCreateView(CycleBaseView, CreateView):
#     """View to create a new Departement"""
# class CycleUpdateView(CycleBaseView, UpdateView):
#     """View to update a Departement"""
# class CycleDeleteView(CycleBaseView, DeleteView):
#     """View to delete a Departement"""
#
# @login_required
# @permission_required('parametrage.view_cycle')
# def cycle_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'cycle.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
#
# class PromotionBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Promotion
#     fields = '__all__'
#     success_url = reverse_lazy('parametrage:promotion')
#     def _formatcss(self,fr,f):
#         fr.fields[f].widget.attrs["class"] = "form-control"
#
#     def _formatcssnonrequired(self,fr,f):
#
#         for x in fr.fields:
#             if x not in f:
#                 fr.fields[x].widget.attrs["required"] = "true"
#
#     def _formatcssdate(self,fr,f):
#         for x in f:
#             fr.fields[x].widget = DateInput(
#             format=('%Y-%m-%d'), attrs={
#                 'type': 'date',
#                     'class':"form-control"
#             })
#
#     def get_form(self, *args, **kwargs):
#         form = super(PromotionBaseView, self).get_form(*args, **kwargs)
#         # form.fields['etablissement'].queryset=Etablissement.objects.all().order_by('nom')
#
#         [self._formatcss(form,f) for f in form.fields]
#         self._formatcssnonrequired(form, [])
#
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:promotion_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:promotion_create')
#         else:
#             url = reverse_lazy('parametrage:promotion')
#         return url
#
#
# class PromotionListView(PromotionBaseView, ListView):
#     """View to list all Departements.
#     Use the 'departement_list' variable in the template
#     to access all Departement objects"""
# class PromotionDetailView(PromotionBaseView, DetailView):
#     """View to list the details from one Departement.
#     Use the 'Departement' variable in the template to access
#     the specific Departement here and in the Views below"""
# class PromotionCreateView(PromotionBaseView, CreateView):
#     """View to create a new Departement"""
# class PromotionUpdateView(PromotionBaseView, UpdateView):
#     """View to update a Departement"""
# class PromotionDeleteView(PromotionBaseView, DeleteView):
#     """View to delete a Departement"""
#
# @login_required
# @permission_required('parametrage.view_promotion')
# def promotion_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'promotion.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
#
# class AnneeacademiqueBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Anneeacademique
#     fields = '__all__'
#     success_url = reverse_lazy('parametrage:anneeacademique')
#     def _formatcss(self,fr,f):
#         fr.fields[f].widget.attrs["class"] = "form-control"
#
#     def _formatcssnonrequired(self,fr,f):
#
#         for x in fr.fields:
#             if x not in f:
#                 fr.fields[x].widget.attrs["required"] = "true"
#
#     def _formatcssdate(self,fr,f):
#         for x in f:
#             fr.fields[x].widget = DateInput(
#             format=('%Y-%m-%d'), attrs={
#                 'type': 'date',
#                     'class':"form-control"
#             })
#
#     def get_form(self, *args, **kwargs):
#         form = super(AnneeacademiqueBaseView, self).get_form(*args, **kwargs)
#         # form.fields['etablissement'].queryset=Etablissement.objects.all().order_by('nom')
#
#         [self._formatcss(form,f) for f in form.fields]
#         self._formatcssnonrequired(form, [])
#         self._formatcssdate(form, ["date_debut",'date_fin'])
#
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:anneeacademique_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:anneeacademique_create')
#         else:
#             url = reverse_lazy('parametrage:anneeacademique')
#         return url
#
#
# class AnneeacademiqueListView(AnneeacademiqueBaseView, ListView):
#     """View to list all Departements.
#     Use the 'departement_list' variable in the template
#     to access all Departement objects"""
# class AnneeacademiqueDetailView(AnneeacademiqueBaseView, DetailView):
#     """View to list the details from one Departement.
#     Use the 'Departement' variable in the template to access
#     the specific Departement here and in the Views below"""
# class AnneeacademiqueCreateView(AnneeacademiqueBaseView, CreateView):
#     """View to create a new Departement"""
# class AnneeacademiqueUpdateView(AnneeacademiqueBaseView, UpdateView):
#     """View to update a Departement"""
# class AnneeacademiqueDeleteView(AnneeacademiqueBaseView, DeleteView):
#     """View to delete a Departement"""
#
# @login_required
# @permission_required('parametrage.view_anneeacademique')
# def anneeacademique_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'anneeacademique.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
# class SemestreBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Semestre
#     fields = '__all__'
#     success_url = reverse_lazy('parametrage:semestre')
#     def _formatcss(self,fr,f):
#         fr.fields[f].widget.attrs["class"] = "form-control"
#
#     def _formatcssnonrequired(self,fr,f):
#
#         for x in fr.fields:
#             if x not in f:
#                 fr.fields[x].widget.attrs["required"] = "true"
#
#     def _formatcssdate(self,fr,f):
#         for x in f:
#             fr.fields[x].widget = DateInput(
#             format=('%Y-%m-%d'), attrs={
#                 'type': 'date',
#                     'class':"form-control"
#             })
#
#     def get_form(self, *args, **kwargs):
#         form = super(SemestreBaseView, self).get_form(*args, **kwargs)
#         # form.fields['etablissement'].queryset=Etablissement.objects.all().order_by('nom')
#
#         [self._formatcss(form,f) for f in form.fields]
#         self._formatcssnonrequired(form, [])
#
#
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:semestre_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:semestre_create')
#         else:
#             url = reverse_lazy('parametrage:semestre')
#         return url
#
#
# class  SemestreListView( SemestreBaseView, ListView):
#     """View to list all Departements.
#     Use the 'departement_list' variable in the template
#     to access all Departement objects"""
# class  SemestreDetailView( SemestreBaseView, DetailView):
#     """View to list the details from one Departement.
#     Use the 'Departement' variable in the template to access
#     the specific Departement here and in the Views below"""
# class  SemestreCreateView( SemestreBaseView, CreateView):
#     """View to create a new Departement"""
# class SemestreUpdateView( SemestreBaseView, UpdateView):
#     """View to update a Departement"""
# class  SemestreDeleteView( SemestreBaseView, DeleteView):
#     """View to delete a Departement"""
#
# @login_required
# @permission_required('parametrage.view_semestre')
# def semestre_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'semestre.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
# class TypefraisBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Typefrais
#     fields = '__all__'
#     success_url = reverse_lazy('parametrage:typefrais')
#     def _formatcss(self,fr,f):
#         fr.fields[f].widget.attrs["class"] = "form-control"
#
#     def _formatcssnonrequired(self,fr,f):
#
#         for x in fr.fields:
#             if x not in f:
#                 fr.fields[x].widget.attrs["required"] = "true"
#
#     def _formatcssdate(self,fr,f):
#         for x in f:
#             fr.fields[x].widget = DateInput(
#             format=('%Y-%m-%d'), attrs={
#                 'type': 'date',
#                     'class':"form-control"
#             })
#
#     def get_form(self, *args, **kwargs):
#         form = super(TypefraisBaseView, self).get_form(*args, **kwargs)
#         # form.fields['etablissement'].queryset=Etablissement.objects.all().order_by('nom')
#
#         [self._formatcss(form,f) for f in form.fields]
#         self._formatcssnonrequired(form, [])
#
#
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:typefrais_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:typefrais_create')
#         else:
#             url = reverse_lazy('parametrage:typefrais')
#         return url
#
#
# class  TypefraisListView( TypefraisBaseView, ListView):
#     """View to list all Departements.
#     Use the 'departement_list' variable in the template
#     to access all Departement objects"""
# class  TypefraisDetailView( TypefraisBaseView, DetailView):
#     """View to list the details from one Departement.
#     Use the 'Departement' variable in the template to access
#     the specific Departement here and in the Views below"""
# class  TypefraisCreateView( TypefraisBaseView, CreateView):
#     """View to create a new Departement"""
# class TypefraisUpdateView( TypefraisBaseView, UpdateView):
#     """View to update a Departement"""
# class  TypefraisDeleteView( TypefraisBaseView, DeleteView):
#     """View to delete a Departement"""
#
# @login_required
# @permission_required('parametrage.view_typefrais')
# def typefrais_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'typefrais.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
#
#
#
# class FraisBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Frais
#     fields = '__all__'
#     success_url = reverse_lazy('parametrage:frais')
#     def _formatcss(self,fr,f):
#         fr.fields[f].widget.attrs["class"] = "form-control"
#
#     def _formatcssnonrequired(self,fr,f):
#
#         for x in fr.fields:
#             if x not in f:
#                 fr.fields[x].widget.attrs["required"] = "true"
#
#     def _formatcssdate(self,fr,f):
#         for x in f:
#             fr.fields[x].widget = DateInput(
#             format=('%Y-%m-%d'), attrs={
#                 'type': 'date',
#                     'class':"form-control"
#             })
#
#     def get_form(self, *args, **kwargs):
#         form = super(FraisBaseView, self).get_form(*args, **kwargs)
#         # form.fields['etablissement'].queryset=Etablissement.objects.all().order_by('nom')
#
#         [self._formatcss(form,f) for f in form.fields]
#         self._formatcssnonrequired(form, [])
#         form.fields["anneeid"].widget.attrs["class"] = "form-control select"
#         form.fields["promotionid"].widget.attrs["class"] = "form-control select"
#         form.fields["typefraisid"].widget.attrs["class"] = "form-control select"
#
#
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:frais_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:frais_create')
#         else:
#             url = reverse_lazy('parametrage:frais')
#         return url
#
#
# class  FraisListView( FraisBaseView, ListView):
#     """View to list all Departements.
#     Use the 'departement_list' variable in the template
#     to access all Departement objects"""
# class  FraisDetailView( FraisBaseView, DetailView):
#     """View to list the details from one Departement.
#     Use the 'Departement' variable in the template to access
#     the specific Departement here and in the Views below"""
# class  FraisCreateView( FraisBaseView, CreateView):
#     """View to create a new Departement"""
# class FraisUpdateView( FraisBaseView, UpdateView):
#     """View to update a Departement"""
# class  FraisDeleteView( FraisBaseView, DeleteView):
#     """View to delete a Departement"""
#
# @login_required
# @permission_required('parametrage.view_frais')
# def frais_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'frais.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
#
# class FonctionBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Fonction
#     fields = '__all__'
#     raise_exception = True
#     success_url = reverse_lazy('parametrage:fonction')
#
#     def get_form(self, *args, **kwargs):
#         form = super(FonctionBaseView, self).get_form(*args, **kwargs)
#         form.fields["libelle"].widget.attrs["class"] = "form-control"
#         form.fields["libelle"].widget.attrs["placeholder"] = "Nom fonction"
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:fonction_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:fonction_create')
#         else:
#             url = reverse_lazy('parametrage:fonction')
#         return url
#
#
# class FonctionListView(FonctionBaseView, ListView):
#     pass
# class FonctionDetailView(FonctionBaseView, DetailView):
#     pass
# class FonctionCreateView(FonctionBaseView, CreateView):
#     pass
# class FonctionUpdateView(FonctionBaseView, UpdateView):
#     pass
# class FonctionDeleteView(FonctionBaseView, DeleteView):
#     pass
# @login_required
# @permission_required('parametrage.view_fonction')
# def fonction_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'fonction.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
#
# class CategorieagentBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Categorieagent
#     fields = '__all__'
#     raise_exception = True
#     success_url = reverse_lazy('parametrage:categorieagent')
#
#     def get_form(self, *args, **kwargs):
#         form = super(CategorieagentBaseView, self).get_form(*args, **kwargs)
#         form.fields["libelle"].widget.attrs["class"] = "form-control"
#         form.fields["libelle"].widget.attrs["required"] = "true"
#         form.fields["isdeleted"].widget.attrs["class"] = "form-control select"
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:categorieagent_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:categorieagent_create')
#         else:
#             url = reverse_lazy('parametrage:categorieagent')
#         return url
#
# class CategorieagentListView(CategorieagentBaseView, ListView):
#     pass
# class CategorieagentDetailView(CategorieagentBaseView, DetailView):
#     pass
# class CategorieagentCreateView(CategorieagentBaseView, CreateView):
#     pass
# class CategorieagentUpdateView(CategorieagentBaseView, UpdateView):
#     pass
# class CategorieagentDeleteView(CategorieagentBaseView, DeleteView):
#     pass
#
# @login_required
# @permission_required('parametrage.view_categorieagent')
# def categorieagent_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'categorieagent.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
# #
# # class AgentBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
# #     model = Agent
# #     fields = '__all__'
# #
# #
# #     raise_exception = True
# #     success_url = reverse_lazy('parametrage:agent')
# #
# #     def _formatcss(self,fr,f):
# #         fr.fields[f].widget.attrs["class"] = "form-control"
# #
# #     def _formatcssnonrequired(self,fr,f):
# #
# #         for x in fr.fields:
# #             if x not in f:
# #                 fr.fields[x].widget.attrs["required"] = "true"
# #
# #     def _formatcssdate(self,fr,f):
# #         for x in f:
# #             fr.fields[x].widget = DateInput(
# #             format=('%Y-%m-%d'), attrs={
# #                 'type': 'date',
# #                     'class':"form-control"
# #             })
# #
# #     def get_form(self, *args, **kwargs):
# #         form = super(AgentBaseView, self).get_form(*args, **kwargs)
# #         # form.fields['etablissement'].queryset=Etablissement.objects.all().order_by('nom')
# #
# #         [self._formatcss(form,f) for f in form.fields]
# #         self._formatcssnonrequired(form, ['email'])
# #         self._formatcssdate(form, ['dateengagement','datenaissance'])
# #         form.fields["categoriagent"].widget.attrs["class"] = "form-control select"
# #         return form
# #
# #     def get_success_url(self):
# #         if '_continue' in self.request.POST:
# #             # ets = self.request.POST['etablissement']
# #             # cat = self.request.POST['categorie']
# #             # ft = self.request.POST['fonction']
# #             #
# #             # AgentCategorie.objects.create(
# #             #     agentid_id=self.object.pk,
# #             #     categorieid_id=cat,
# #             #     date_debut=datetime.date.today(),
# #             # )
# #             #
# #             # AgentFonction.objects.create(
# #             #     agentid_id=self.object.pk,
# #             #     fonctionid_id=ft,
# #             #     date_debut=datetime.date.today(),
# #             # )
# #             url = reverse_lazy('parametrage:agent_update', kwargs={'pk': self.object.pk}, )
# #         elif '_addanother' in self.request.POST:
# #             # ets = self.request.POST['etablissement']
# #             # cat = self.request.POST['categorie']
# #             # ft = self.request.POST['fonction']
# #             #
# #             # AgentCategorie.objects.create(
# #             #     agentid_id=self.object.pk,
# #             #     categorieid_id=cat,
# #             #     date_debut =datetime.date.today(),
# #             #                      )
# #             #
# #             # AgentFonction.objects.create(
# #             #     agentid_id=self.object.pk,
# #             #     fonctionid_id=ft,
# #             #     date_debut =datetime.date.today(),
# #             #                         )
# #             url = reverse_lazy('parametrage:agent_create')
# #         elif '_save' in self.request.POST:
# #             # ets = self.request.POST['etablissement']
# #             # cat = self.request.POST['categorie']
# #             # ft = self.request.POST['fonction']
# #             #
# #             # AgentCategorie.objects.create(
# #             #     agentid_id=self.object.pk,
# #             #     categorieid_id=cat,
# #             #     date_debut=datetime.date.today(),
# #             # )
# #             #
# #             # AgentFonction.objects.create(
# #             #     agentid_id=self.object.pk,
# #             #     fonctionid_id=ft,
# #             #     date_debut=datetime.date.today(),
# #             # )
# #             url = reverse_lazy('parametrage:agent')
# #         else:
# #             url = reverse_lazy('parametrage:agent')
# #         return url
# #
# #     def form_valid(self, form):
# #         # self.object = form.save(commit=False)
# #         # self.object.created_by_user = self.request.user
# #         # self.object.save()
# #         return super().form_valid(form)
# #
# #     def get_context_data(self, **kwargs):
# #         context = super().get_context_data(**kwargs)
# #
# #         # context["etablissements"] = Etablissement.objects.all().order_by('nom')
# #         # context["fonctions"] = Fonction.objects.all().order_by('libelle')
# #         # context["categories"] = Categorieagent.objects.all().order_by('libelle')
# #         return context
# #
# # class AgentListView(AgentBaseView, ListView):
# #     pass
# # class AgentDetailView(AgentBaseView, DetailView):
# #     pass
# # class AgentCreateView(AgentBaseView, CreateView):
# #     pass
# # class AgentUpdateView(AgentBaseView, UpdateView):
# #     pass
# #     # def get_context_data(self, **kwargs):
# #     #     context = super().get_context_data(**kwargs)
# #     #     # context["etablissementsid"] = 1
# #     #     context["fonctionsid"] = AgentFonction.objects.get(agentid_id=self.object.pk).fonctionid.id
# #     #     context["categorieid"] = AgentCategorie.objects.get(agentid_id=self.object.pk).categorieid.id
# #     #
# #     #
# #     #     return context
# # class AgentDeleteView(AgentBaseView, DeleteView):
# #     pass
# #     # def delete(self, request, *args, **kwargs):
# #     #     self.object = self.get_object()
# #     #     if self.object.agentcategorie_set.exists():
# #     #         AgentCategorie.objects.filter(
# #     #             agentid_id=self.object.pk,
# #     #         ).delete()
# #     #     if self.object.agentfonction_set.exists():
# #     #         AgentFonction.objects.filter(
# #     #             agentid_id=self.object.pk,
# #     #         ).delete()
# #     #     # success_url = self.get_success_url()
# #     #     #self.object.update(isdeleted=False)
# #     #     # return HttpResponseRedirect(success_url)
# #     #     return super(AgentDeleteView, self).delete(request, *args, **kwargs)
# #
# # @login_required
# # @permission_required('parametrage.view_agent')
# # def agent_rapport(request):
# #     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# #     input_file=os.path.join(fn,'agent.jrxml')
# #     output_file=os.path.join(fn,'media')
# #
# #     con={
# #         'driver':'generic',
# #         'jdbc_driver':'org.postgresql.Driver',
# #         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
# #         'jdbc_dir':fn,
# #         'username':settings.DATABASES['default']['USER'],
# #         'password':settings.DATABASES['default']['PASSWORD'],
# #
# #     }
# #     jasper=JasperPy()
# #     jasper.process(
# #         input_file,
# #         output_file,
# #         format_list=["pdf"],
# #         db_connection=con,
# #         #parameters={},
# #         locale='en_US'
# #     )
# #     return HttpResponse('true')
# #
#
#
# class AgentCategorieBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = AgentCategorie
#     fields = '__all__'
#     raise_exception = True
#     success_url = reverse_lazy('parametrage:agentcategorie')
#
#     def _formatcss(self,fr,f):
#         fr.fields[f].widget.attrs["class"] = "form-control"
#
#     def _formatcssnonrequired(self,fr,f):
#
#         for x in fr.fields:
#             if x not in f:
#                 fr.fields[x].widget.attrs["required"] = "true"
#
#     def _formatcssdate(self,fr,f):
#         for x in f:
#             fr.fields[x].widget = DateInput(
#             format=('%Y-%m-%d'), attrs={
#                 'type': 'date',
#                     'class':"form-control"
#             })
#
#     def get_form(self, *args, **kwargs):
#         form = super(AgentCategorieBaseView, self).get_form(*args, **kwargs)
#
#         [self._formatcss(form, f) for f in form.fields]
#         self._formatcssnonrequired(form, ['date_fin','isdeleted'])
#         self._formatcssdate(form, ['date_debut', 'date_fin'])
#         form.fields["agentid"].widget.attrs["class"] = "form-control select"
#         form.fields["categorieid"].widget.attrs["class"] = "form-control select"
#
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:agentcategorie_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:agentcategorie_create')
#         else:
#             url = reverse_lazy('parametrage:agentcategorie')
#         return url
#
# class AgentCategorieListView(AgentCategorieBaseView, ListView):
#     pass
# class AgentCategorieDetailView(AgentCategorieBaseView, DetailView):
#     pass
# class AgentCategorieCreateView(AgentCategorieBaseView, CreateView):
#     pass
# class AgentCategorieUpdateView(AgentCategorieBaseView, UpdateView):
#     pass
# class AgentCategorieDeleteView(AgentCategorieBaseView, DeleteView):
#     pass
#
# @login_required
# @permission_required('parametrage.view_agentcategorie')
# def agentcategorie_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'agentcategorie.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
#
# class AgentFonctionBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = AgentFonction
#     fields = '__all__'
#     raise_exception = True
#     success_url = reverse_lazy('parametrage:agentfonction')
#
#     def _formatcss(self,fr,f):
#         fr.fields[f].widget.attrs["class"] = "form-control"
#
#     def _formatcssnonrequired(self,fr,f):
#
#         for x in fr.fields:
#             if x not in f:
#                 fr.fields[x].widget.attrs["required"] = "true"
#
#     def _formatcssdate(self,fr,f):
#         for x in f:
#             fr.fields[x].widget = DateInput(
#             format=('%Y-%m-%d'), attrs={
#                 'type': 'date',
#                     'class':"form-control"
#             })
#
#     def get_form(self, *args, **kwargs):
#         form = super(AgentFonctionBaseView, self).get_form(*args, **kwargs)
#
#         [self._formatcss(form, f) for f in form.fields]
#         self._formatcssnonrequired(form, ['date_fin','isdeleted','ref_decision_fonction'])
#         self._formatcssdate(form, ['date_debut', 'date_fin'])
#         form.fields["agentid"].widget.attrs["class"] = "form-control select"
#         form.fields["fonctionid"].widget.attrs["class"] = "form-control select"
#
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:agentfonction_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:agentfonction_create')
#         else:
#             url = reverse_lazy('parametrage:agentfonction')
#         return url
#
# class AgentFonctionListView(AgentFonctionBaseView, ListView):
#     pass
# class AgentFonctionDetailView(AgentFonctionBaseView, DetailView):
#     pass
# class AgentFonctionCreateView(AgentFonctionBaseView, CreateView):
#     pass
# class AgentFonctionUpdateView(AgentFonctionBaseView, UpdateView):
#     pass
# class AgentFonctionDeleteView(AgentFonctionBaseView, DeleteView):
#     pass
#
# @login_required
# @permission_required('parametrage.view_agentfonction')
# def agentfonction_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'agentfonction.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
#
#
#
#
#
#
# #categorieetablissement###############################################################################################typeetablissement
# class CategorieetablissementBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Categorieetablissement
#     fields = '__all__'
#     raise_exception = True
#     success_url = reverse_lazy('parametrage:categorieetablissement')
#
#     def get_form(self, *args, **kwargs):
#         form = super(CategorieetablissementBaseView, self).get_form(*args, **kwargs)
#         form.fields["nom"].widget.attrs["class"] = "form-control"
#         form.fields["nom"].widget.attrs["required"] = "true"
#         form.fields["isdeleted"].widget.attrs["class"] = "form-control select"
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:categorieetablissement_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:categorieetablissement_create')
#         else:
#             url = reverse_lazy('parametrage:categorieetablissement')
#         return url
#
# class CategorieetablissementListView(CategorieetablissementBaseView, ListView):
#     pass
# class CategorieetablissementDetailView(CategorieetablissementBaseView, DetailView):
#     pass
# class CategorieetablissementCreateView(CategorieetablissementBaseView, CreateView):
#     pass
# class CategorieetablissementUpdateView(CategorieetablissementBaseView, UpdateView):
#     pass
# class CategorieetablissementDeleteView(CategorieetablissementBaseView, DeleteView):
#     pass
#
# @login_required
# @permission_required('parametrage.view_categorieetablissement')
# def categorieetablissement_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'categorieetablissement.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
# #categorieetablissement##############################################################################################typeetablissement
#
# #typeetablissement###############################################################################################typeetablissement
# class TypeetablissementBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Typeetablissement
#     fields = '__all__'
#     raise_exception = True
#     success_url = reverse_lazy('parametrage:typeetablissement')
#
#     def get_form(self, *args, **kwargs):
#         form = super(TypeetablissementBaseView, self).get_form(*args, **kwargs)
#         form.fields["libelle"].widget.attrs["class"] = "form-control"
#         form.fields["libelle"].widget.attrs["required"] = "true"
#         form.fields["isdeleted"].widget.attrs["class"] = "form-control select"
#         form.fields["catid"].widget.attrs["class"] = "form-control select"
#         # form.fields["catid"].queryset = Categorieetablissement.objects.filter(id=2)
#
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:typeetablissement_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:typeetablissement_create')
#         else:
#             url = reverse_lazy('parametrage:typeetablissement')
#         return url
#
# class TypeetablissementListView(TypeetablissementBaseView, ListView):
#     pass
# class TypeetablissementDetailView(TypeetablissementBaseView, DetailView):
#     pass
# class TypeetablissementCreateView(TypeetablissementBaseView, CreateView):
#     pass
# class TypeetablissementUpdateView(TypeetablissementBaseView, UpdateView):
#     pass
# class TypeetablissementDeleteView(TypeetablissementBaseView, DeleteView):
#     pass
#
# @login_required
# @permission_required('parametrage.view_typeetablissement')
# def typeetablissement_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'typeetablissement.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
# #typeetablissement##############################################################################################typeetablissement
#
# class ProvinceBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Province
#     fields = '__all__'
#     raise_exception = True
#     success_url = reverse_lazy('parametrage:province')
#
#     def get_form(self, *args, **kwargs):
#         form = super(ProvinceBaseView, self).get_form(*args, **kwargs)
#         form.fields["nom"].widget.attrs["class"] = "form-control"
#         form.fields["nom"].widget.attrs["placeholder"] = "Nom province"
#         form.fields["codeprovince"].widget.attrs["class"] = "form-control"
#         form.fields["codeprovince"].widget.attrs["required"] = "true"
#         form.fields["nom"].widget.attrs["required"] = "true"
#         form.fields["codeprovince"].widget.attrs["placeholder"] = "Code province"
#         return form
#
#
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:province_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:province_create')
#         else:
#             url = reverse_lazy('parametrage:province')
#         return url
#
# class ProvinceListView(ProvinceBaseView, ListView):
#     pass
# class ProvinceDetailView(ProvinceBaseView, DetailView):
#     pass
# class ProvinceCreateView(ProvinceBaseView, CreateView):
#     pass
# class ProvinceUpdateView(ProvinceBaseView, UpdateView):
#     pass
# class ProvinceDeleteView(ProvinceBaseView, DeleteView):
#     pass
#
# @login_required
# @permission_required('parametrage.view_province')
# def province_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'province.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
# class TerritoirevilleBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Territoireville
#     fields = '__all__'
#     raise_exception = True
#     success_url = reverse_lazy('parametrage:territoireville')
#
#     def get_form(self, *args, **kwargs):
#         form = super(TerritoirevilleBaseView, self).get_form(*args, **kwargs)
#         form.fields["isdeleted"].widget.attrs["class"] = "form-control select"
#         form.fields["libelle"].widget.attrs["class"] = "form-control"
#         form.fields["libelle"].widget.attrs["placeholder"] = "Nom territoire"
#         form.fields["libelle"].widget.attrs["required"] = "true"
#         form.fields["provinceid"].widget.attrs["class"] = "form-control select"
#         form.fields["provinceid"].widget.attrs["required"] = "true"
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:territoireville_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:territoireville_create')
#         else:
#             url = reverse_lazy('parametrage:territoireville')
#         return url
#
# class TerritoirevilleListView(TerritoirevilleBaseView, ListView):
#     pass
# class TerritoirevilleDetailView(TerritoirevilleBaseView, DetailView):
#     pass
# class TerritoirevilleCreateView(TerritoirevilleBaseView, CreateView):
#     pass
# class TerritoirevilleUpdateView(TerritoirevilleBaseView, UpdateView):
#     pass
# class TerritoirevilleDeleteView(TerritoirevilleBaseView, DeleteView):
#     pass
#
# @login_required
# @permission_required('parametrage.view_territoireville')
# def territoireville_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'territoireville.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
#
# class EtablissementBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Etablissement
#     fields = '__all__'
#     raise_exception = True
#     success_url = reverse_lazy('parametrage:etablissement')
#
#     def get_form(self, *args, **kwargs):
#         form = super(EtablissementBaseView, self).get_form(*args, **kwargs)
#
#         form.fields["sigle"].widget.attrs= {'required': 'true', 'class': 'form-control'}
#         form.fields["nom"].widget.attrs= {'required': 'true', 'class': 'form-control'}
#         form.fields["typeid"].widget.attrs= {'required': 'true', 'class': 'form-control'}
#         form.fields["adresse"].widget.attrs= {'required': 'true', 'class': 'form-control'}
#         form.fields["siteinternet"].widget.attrs["class"] = "form-control"
#
#         form.fields["datecreation"].widget= DateInput(
#                 format=('%Y-%m-%d'), attrs={
#                     'class': 'form-control',
#                     'type': 'date'
#                 })
#
#         form.fields["telephone"].widget.attrs= {'required': 'true', 'class': 'form-control'}
#         form.fields["email"].widget.attrs["class"] = "form-control"
#         form.fields["territoirid"].widget.attrs= {'required': 'true', 'class': 'form-control'}
#         form.fields["isdeleted"].widget.attrs["class"] = "form-control"
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:etablissement_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:etablissement_create')
#         else:
#             url = reverse_lazy('parametrage:etablissement')
#         return url
#
# class EtablissementListView(EtablissementBaseView, ListView):
#     pass
# class EtablissementDetailView(EtablissementBaseView, DetailView):
#     pass
# class EtablissementCreateView(EtablissementBaseView, CreateView):
#     pass
# class EtablissementUpdateView(EtablissementBaseView, UpdateView):
#     pass
# class EtablissementDeleteView(EtablissementBaseView, DeleteView):
#     pass
#
# @login_required
# @permission_required('parametrage.view_etablissement')
# def etablissement_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'etablissement.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
#
#
# class CoursBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Cours
#     fields = '__all__'
#     raise_exception = True
#     success_url = reverse_lazy('parametrage:cours')
#
#     def _formatcss(self, fr, f):
#         fr.fields[f].widget.attrs["class"] = "form-control"
#
#     def _formatcssnonrequired(self, fr, f):
#
#         for x in fr.fields:
#             if x not in f:
#                 fr.fields[x].widget.attrs["required"] = "true"
#
#     def _formatcssdate(self, fr, f):
#         for x in f:
#             fr.fields[x].widget = DateInput(
#                 format=('%Y-%m-%d'), attrs={
#                     'type': 'date',
#                     'class': "form-control"
#                 })
#     def get_form(self, *args, **kwargs):
#         form = super(CoursBaseView, self).get_form(*args, **kwargs)
#
#
#         [self._formatcss(form, f) for f in form.fields]
#
#
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:cours_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:cours_create')
#         else:
#             url = reverse_lazy('parametrage:cours')
#         return url
#
#
# class CoursListView(CoursBaseView, ListView):
#     pass
# class CoursDetailView(CoursBaseView, DetailView):
#     pass
# class CoursCreateView(CoursBaseView, CreateView):
#     pass
# class CoursUpdateView(CoursBaseView, UpdateView):
#     pass
# class CoursDeleteView(CoursBaseView, DeleteView):
#     pass
# @login_required
# @permission_required('parametrage.view_cours')
# def cours_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'cours.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
#
# class SessionBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Session
#     fields = '__all__'
#     raise_exception = True
#     success_url = reverse_lazy('parametrage:session')
#
#     def _formatcss(self, fr, f):
#         fr.fields[f].widget.attrs["class"] = "form-control"
#
#     def _formatcssnonrequired(self, fr, f):
#
#         for x in fr.fields:
#             if x not in f:
#                 fr.fields[x].widget.attrs["required"] = "true"
#
#     def _formatcssdate(self, fr, f):
#         for x in f:
#             fr.fields[x].widget = DateInput(
#                 format=('%Y-%m-%d'), attrs={
#                     'type': 'date',
#                     'class': "form-control"
#                 })
#     def get_form(self, *args, **kwargs):
#         form = super(SessionBaseView, self).get_form(*args, **kwargs)
#
#
#         [self._formatcss(form, f) for f in form.fields]
#
#
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:session_update', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:session_create')
#         else:
#             url = reverse_lazy('parametrage:session')
#         return url
#
#
# class SessionListView(SessionBaseView, ListView):
#     pass
# class SessionDetailView(SessionBaseView, DetailView):
#     pass
# class SessionCreateView(SessionBaseView, CreateView):
#     pass
# class SessionUpdateView(SessionBaseView, UpdateView):
#     pass
# class SessionDeleteView(SessionBaseView, DeleteView):
#     pass
# @login_required
# @permission_required('parametrage.view_session')
# def session_rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'session.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/'+str(settings.DATABASES['default']['NAME']),
#         'jdbc_dir':fn,
#         'username':settings.DATABASES['default']['USER'],
#         'password':settings.DATABASES['default']['PASSWORD'],
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
#
#
# #Super class
# class RHBaseViewConge(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Conge
#     fields = '__all__'
#     raise_exception = True
#     success_url = reverse_lazy('parametrage:parametrage')
#
#     def get_form(self, *args, **kwargs):
#         form = super(RHBaseViewConge, self).get_form(*args, **kwargs)
#         # form(initial={'userid':self.request.user})
#         form.fields["libelle"].widget.attrs["class"] = "form-control"
#         form.fields["libelle"].widget.attrs["placeholder"] = "Libelle congé"
#         form.fields["libelle"].widget.attrs["required"] = "true"
#
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:CongeUpdateView', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:CongeCreateView')
#         else:
#             url = reverse_lazy('parametrage:CongeListView')
#         return url
#
#
# #Liste des etudiants inscript
# class CongeListView(RHBaseViewConge, ListView):
#     # print("fddfdfdd")
#     template_name = "parametrage/conge_list.html"
#     #context_object_name ='etudiants_list'
#
# class CongeDetailView(RHBaseViewConge, DetailView):
#     template_name = "parametrage/conge_detail.html"
#
# class CongeCreateView(RHBaseViewConge, CreateView):
#     template_name = "parametrage/conge_form.html"
#
# class CongeUpdateView(RHBaseViewConge, UpdateView):
#     template_name = "parametrage/conge_form.html"
#
# class CongeDeleteView(RHBaseViewConge, DeleteView):
#     template_name = "parametrage/conge_confirm_delete.html"
#
# @login_required
# @permission_required('parametrage.view_Conge')
# def Conge_Rapport(request):
#     fn=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     input_file=os.path.join(fn,'liste_des_conges.jrxml')
#     output_file=os.path.join(fn,'media')
#
#     con={
#         'driver':'generic',
#         'jdbc_driver':'org.postgresql.Driver',
#         'jdbc_url':'jdbc:postgresql://localhost:5432/ESU_DATA',
#         'jdbc_dir':fn,
#         'username':'postgres',
#         'password':'shongo2019',
#
#     }
#     jasper=JasperPy()
#     jasper.process(
#         input_file,
#         output_file,
#         format_list=["pdf"],
#         db_connection=con,
#         #parameters={},
#         locale='en_US'
#     )
#     return HttpResponse('true')
#
#
#
# #Super class
# class RHBaseViewService(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Services
#     fields = '__all__'
#     raise_exception = True
#     success_url = reverse_lazy('parametrage:parametrage')
#
#     def get_form(self, *args, **kwargs):
#         form = super(RHBaseViewService, self).get_form(*args, **kwargs)
#         # form(initial={'userid':self.request.user})
#         form.fields["libelle"].widget.attrs["class"] = "form-control"
#         form.fields["libelle"].widget.attrs["placeholder"] = "Libelle service"
#         form.fields["libelle"].widget.attrs["required"] = "true"
#
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:ServiceUpdateView', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:ServiceCreateView')
#         else:
#             url = reverse_lazy('parametrage:ServicesListView')
#         return url
#
#
# #Liste des etudiants inscript
# class ServicesListView(RHBaseViewService, ListView):
#     # print("fddfdfdd")
#     template_name = "parametrage/services_list.html"
#     #context_object_name ='etudiants_list'
#
#
#
# class ServiceDetailView(RHBaseViewService, DetailView):
#     template_name = "parametrage/services_detail.html"
#
# class ServiceCreateView(RHBaseViewService, CreateView):
#     template_name = "parametrage/services_form.html"
#
# class ServiceUpdateView(RHBaseViewService, UpdateView):
#     template_name = "parametrage/services_form.html"
#
# class ServiceDeleteView(RHBaseViewService, DeleteView):
#     template_name = "parametrage/services_confirm_delete.html"
#
#
# #Super class
# class RHBaseViewdoc(LoginRequiredMixin,PermissionRequiredMixin,View):
#     model = Typedocument
#     fields = '__all__'
#     raise_exception = True
#     success_url = reverse_lazy('parametrage:CategoriedocumentListView')
#
#     def get_form(self, *args, **kwargs):
#         form = super(RHBaseViewdoc, self).get_form(*args, **kwargs)
#         # form(initial={'userid':self.request.user})
#         form.fields["nom_type_document"].widget.attrs["class"] = "form-control"
#         form.fields["nom_type_document"].widget.attrs["placeholder"] = "Libelle document"
#         form.fields["nom_type_document"].widget.attrs["required"] = "true"
#
#         return form
#
#     def get_success_url(self):
#         if '_continue' in self.request.POST:
#             url = reverse_lazy('parametrage:CategoriedocumentUpdateView', kwargs={'pk': self.object.pk}, )
#         elif '_addanother' in self.request.POST:
#             url = reverse_lazy('parametrage:CategoriedocumentCreateView')
#         else:
#             url = reverse_lazy('parametrage:CategoriedocumentListView')
#         return url
#
#
# #Liste des etudiants inscript
# class CategoriedocumentListView(RHBaseViewdoc, ListView):
#     # print("fddfdfdd")
#     template_name = "parametrage/typedocument_list.html"
#     #context_object_name ='etudiants_list'
#
#
# class CategoriedocumentDetailView(RHBaseViewdoc, DetailView):
#     template_name = "parametrage/typedocument_detail.html"
#
# class CategoriedocumentCreateView(RHBaseViewdoc, CreateView):
#     template_name = "parametrage/typedocument_form.html"
#
# class CategoriedocumentUpdateView(RHBaseViewdoc, UpdateView):
#     template_name = "parametrage/typedocument_form.html"
#
# class CategoriedocumentDeleteView(RHBaseViewdoc, DeleteView):
#     template_name = "parametrage/typedocument_confirm_delete.html"
#
#
