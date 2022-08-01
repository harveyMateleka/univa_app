import os
import re
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.storage import FileSystemStorage
from django.db import connection
from django.db.models import Value, CharField, Sum, Max, FloatField, F
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
# Create your views here.
from pyreportjasper import JasperPy

from cote.models import exemplaire, etudprom,cote,tempjournalcote,enseigne,delibe
from django.forms import DateInput

from parametrage.models import promotions, annee, cours, sessions, departements


def mentionFinal(pourc, varleger, vargrave, varvide):
    m=''
    if float(pourc)<=50.0:
        m="A"
    else:
        with connection.cursor() as cursor:
            rqttempo='SELECT * from cote_delibe where de<=%s and a>%s'
            cursor.execute(rqttempo, [float(pourc), float(pourc)])
            rows =cursor.fetchall()
            if len(rows) >= 1:
                IH= 0
                i=0
                tot=(len(rows)/4)

                while i<tot:
                    rqt=rqttempo+f' and position=%s and %s{rows[IH][8]}%s and %s{rows[IH+1][8]}%s and %s{rows[IH+2][8]}%s'

                    cursor.execute(rqt, [float(pourc), float(pourc),int(i+1), int(varleger),int(rows[IH][9]), int(vargrave),int(rows[IH+1][9]), int(varvide),int(rows[IH+2][9])])

                    rowst =cursor.fetchall()
                    if len(rowst) >= 1:
                        m=rowst[3][8]
                        break
                    IH += 4
                    i+=1
    return m


def calculerpourcentage(annee,promotion,cours,session,matr):
    listponde={}
    for l in enseigne.objects.filter(promotion_id=promotion,annee_id=annee):
        listponde[l.cours.id]=l.ponderaton


    nbrcours=enseigne.objects.filter(promotion_id=promotion,annee_id=annee).count()
    totponde=enseigne.objects.filter(promotion_id=promotion,annee_id=annee).aggregate(somme=Sum('ponderaton')).get('somme')
    ponde=enseigne.objects.filter(promotion_id=promotion,cours_id=cours,annee_id=annee).aggregate(somme=Sum('ponderaton')).get('somme')
    if ponde is None:
        ponde=0

    if totponde is None:
        totponde=0
    else:
        totponde=totponde*20


    #creation table
    with connection.cursor() as cursor:
        sql = 'CREATE TABLE IF NOT EXISTS "' + str(promotion)+'_'+str(annee) + '" (id serial PRIMARY KEY,matricule VARCHAR (200) UNIQUE NOT NULL,session INT NOT NULL,annee INT NOT NULL,'
        e=enseigne.objects.filter(promotion_id=promotion,annee_id=annee).order_by('-ponderaton').order_by('-heure').order_by('-cours_id')
        for i in e:
            sql += '"'+str(i.cours_id)+'" numeric(10,2) NULL,'
        sql += 'pourc numeric(10,2) NULL,nbrechec INT NULL,nbrechecleger INT NULL,nbrechecgrave INT NULL,nbrevide INT NULL,trav numeric(10,2) NULL,stag numeric(10,2) NULL,mention VARCHAR (2) NULL,mention2 VARCHAR (2) NULL)'
        cursor.execute(sql)
    # creation table

    ##################################recuperer moyen interro/tp
    numinterro=cote.objects.filter(matricule_id=matr,promotion_id=promotion,annee_id=annee,cours_id=cours,sesionn="5").aggregate(nbr=Max('numero')).get('nbr')
    if numinterro is None:
        numinterro=0

    moyinterro=cote.objects.filter(matricule_id=matr,promotion_id=promotion,annee_id=annee,cours_id=cours,sesionn="5").aggregate(somme=Sum('cote')).get('somme')
    if moyinterro is None:
        moyinterro=0
    else:
        moyinterro=float(moyinterro)/float(numinterro)

    numtp = cote.objects.filter(matricule_id=matr, promotion_id=promotion, annee_id=annee, cours_id=cours,sesionn="4").aggregate(nbr=Max('numero')).get('nbr')
    if numtp is None:
        numtp = 0

    moytp = cote.objects.filter(matricule_id=matr, promotion_id=promotion, annee_id=annee, cours_id=cours,sesionn="4").aggregate(somme=Sum('cote')).get('somme')
    if moytp is None:
        moytp = 0
    else:
        moytp = float(moytp) / float(numtp)


    ##################################recuperer moyen interro/tp

    moyexa = float(0)
    somme = float(0)

    if session==4 or session==5:#Tp and Interro
        moyexa1 = cote.objects.filter(matricule_id=matr,promotion_id=promotion,annee_id=annee,cours_id=cours,sesionn="1").aggregate(somme=Sum('cote')).get('somme')#mi-session note
        if moyexa1 is None:
            moyexa1 = 0
        moyexa2 = cote.objects.filter(matricule_id=matr,promotion_id=promotion,annee_id=annee,cours_id=cours,sesionn="2").aggregate(somme=Sum('cote')).get('somme')#1er session note
        if moyexa2 is None:
            moyexa2 = 0
        moyexa3 = cote.objects.filter(matricule_id=matr,promotion_id=promotion,annee_id=annee,cours_id=cours,sesionn="3").aggregate(somme=Sum('cote')).get('somme')#2eme session note
        if moyexa3 is None:
            moyexa3 = 0

        somme1 = float(moyexa1)+float(moyinterro)+float(moytp)
        totgen1 = somme1*float(ponde)
        somme2 =  float(moyexa2)+float(moyinterro)+float(moytp)
        somme3 =  float(moyexa3)+float(moyinterro)+float(moytp)

        #update/add------------------------------------------------

        varvide=varleger=vargrave=0
        mention=''
        pourc=float(0)
        tot=float(0)

        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM "' + str(promotion)+'_'+str(annee) + '" WHERE matricule = %s and annee = %s and session =1', [matr,annee])
            if cursor.rowcount>=1:
                cursor.execute('UPDATE "' + str(promotion)+'_'+str(annee) + '" SET ' + cours+ ' = %s WHERE matricule = %s and annee = %s and session =1', [somme1,matr,annee])

            cursor.execute('SELECT * FROM "' + str(promotion)+'_'+str(annee) + '" WHERE matricule = %s and annee = %s and session =2',[matr, annee])
            if cursor.rowcount >= 1:
                cursor.execute('UPDATE "' + str(promotion)+'_'+str(annee) + '" SET ' + cours+ ' = %s WHERE matricule = %s and annee = %s and session =2', [somme2,matr,annee])

            cursor.execute('SELECT * FROM "' + str(promotion)+'_'+str(annee) + '" WHERE matricule = %s and annee = %s and session =3',[matr, annee])
            if cursor.rowcount >= 1:
                cursor.execute('UPDATE "' + str(promotion)+'_'+str(annee) + '" SET ' + cours+ ' = %s WHERE matricule = %s and annee = %s and session =3', [somme3,matr,annee])

            ##################################################----------------------------mi-session
            cursor.execute('SELECT * FROM "' + str(promotion)+'_'+str(annee) + '" WHERE matricule = %s and annee = %s and session =1',[matr, annee])
            if cursor.rowcount >= 1:
                cmp= nbrcours+4

                varvide = 0
                vargrave = 0
                varleger = 0
                tot=float(0)
                records = cursor.fetchall()
                columns = cursor.description
                i=4
                while i<cmp:
                    if records[0][i] is None:
                        varvide += 0
                    else:
                        ponderationcours=enseigne.objects.filter(promotion_id=promotion,cours_id=int(columns[i][0]),annee_id=annee).aggregate(somme=Sum('ponderaton')).get('somme')
                        if ponderationcours is None:
                            ponderationcours=0
                        tot += float(records[0][i]) * float(ponderationcours)
                        if float(records[0][i]) >= 0 and float(records[0][i]) <= 7.9:
                            vargrave += 1
                        elif float(records[0][i]) >= 8 and float(records[0][i]) <= 10:
                            varleger += 1
                    i+=1
                pourc = float(tot * 100) / float(totponde)
                mention = mentionFinal(pourc, varleger, vargrave, varvide)
                cursor.execute('update "' + str(promotion) + '_' + str(annee) + '" set pourc=%s,nbrechec=%s,nbrechecleger=%s,nbrechecgrave=%s,nbrevide=%s,mention=%s where matricule=%s and session=%s and annee=%s',[ pourc, (varleger + vargrave), varleger, vargrave, varvide, mention,matr, 1, annee])
                return True
            else:
                pourc = float(totgen1 * 100) / float(totponde)
                varvide = nbrcours-1
                vargrave = 0
                varleger = 0

                if somme1 >= 0 and somme1 <= 7.9:
                    vargrave += 1
                elif somme1 >= 8 and somme1 <= 10:
                    varleger += 1
                mention = mentionFinal(pourc, varleger, vargrave, varvide)
                cursor.execute('insert into "' + str(promotion) + '_' + str(annee) + '" (matricule,session,annee,pourc,nbrechec,nbrechecleger,nbrechecgrave,nbrevide,mention,"' + str(cours) + '") values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[matr,1,annee,pourc,(varleger + vargrave),varleger,vargrave,varvide,mention,somme1])
                return True
            ##################################################----------------------------mi-session

            ##################################################----------------------------1er-session
            cursor.execute('SELECT * FROM "' + str(promotion) + '_' + str(
                annee) + '" WHERE matricule = %s and annee = %s and session =2', [matr, annee])
            if cursor.rowcount >= 1:
                cmp = nbrcours + 4

                varvide = 0
                vargrave = 0
                varleger = 0
                tot = float(0)
                records = cursor.fetchall()
                columns = cursor.description
                i = 4
                while i < cmp:
                    if records[0][i] is None:
                        varvide += 0
                    else:
                        ponderationcours = enseigne.objects.filter(promotion_id=promotion,
                                                                   cours_id=int(columns[i][0]),
                                                                   annee_id=annee).aggregate(
                            somme=Sum('ponderaton')).get('somme')
                        if ponderationcours is None:
                            ponderationcours = 0
                        tot += float(records[0][i]) * float(ponderationcours)
                        if float(records[0][i]) >= 0 and float(records[0][i]) <= 7.9:
                            vargrave += 1
                        elif float(records[0][i]) >= 8 and float(records[0][i]) <= 10:
                            varleger += 1
                    i += 1
                pourc = float(tot * 100) / float(totponde)
                mention = mentionFinal(pourc, varleger, vargrave, varvide)
                cursor.execute('update "' + str(promotion) + '_' + str(
                    annee) + '" set pourc=%s,nbrechec=%s,nbrechecleger=%s,nbrechecgrave=%s,nbrevide=%s,mention=%s where matricule=%s and session=%s and annee=%s',
                               [pourc, (varleger + vargrave), varleger, vargrave, varvide, mention, matr, 2, annee])
                return True
            ##################################################----------------------------1er-session

            ##################################################----------------------------2em-session
            cursor.execute('SELECT * FROM "' + str(promotion) + '_' + str(
                annee) + '" WHERE matricule = %s and annee = %s and session =3', [matr, annee])
            if cursor.rowcount >= 1:
                cmp = nbrcours + 4

                varvide = 0
                vargrave = 0
                varleger = 0
                tot = float(0)
                records = cursor.fetchall()
                columns = cursor.description
                i = 4
                while i < cmp:
                    if records[0][i] is None:
                        varvide += 0
                    else:
                        ponderationcours = enseigne.objects.filter(promotion_id=promotion,
                                                                   cours_id=int(columns[i][0]),
                                                                   annee_id=annee).aggregate(
                            somme=Sum('ponderaton')).get('somme')
                        if ponderationcours is None:
                            ponderationcours = 0
                        tot += float(records[0][i]) * float(ponderationcours)
                        if float(records[0][i]) >= 0 and float(records[0][i]) <= 7.9:
                            vargrave += 1
                        elif float(records[0][i]) >= 8 and float(records[0][i]) <= 10:
                            varleger += 1
                    i += 1
                pourc = float(tot * 100) / float(totponde)
                mention = mentionFinal(pourc, varleger, vargrave, varvide)
                cursor.execute('update "' + str(promotion) + '_' + str(
                    annee) + '" set pourc=%s,nbrechec=%s,nbrechecleger=%s,nbrechecgrave=%s,nbrevide=%s,mention=%s where matricule=%s and session=%s and annee=%s',
                               [pourc, (varleger + vargrave), varleger, vargrave, varvide, mention, matr, 3, annee])
                return True
            ##################################################----------------------------2em-session
        #update/add------------------------------------------------

    else:#Examen
        c = cote.objects.filter(matricule_id=matr, promotion_id=promotion, annee_id=annee, cours_id=cours,sesionn=session)
        if c :
            moyexa=c.first().cote
            ponde=ponde
        somme = moyexa + moyinterro + moytp #la somme de tt
        totGen= ponde * somme #la totale pour c cours


        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM "' + str(promotion) + '_' + str(
                annee) + '" WHERE matricule = %s and annee = %s and session =%s', [matr, annee,session])
            if cursor.rowcount >= 1:
                cursor.execute('UPDATE "' + str(promotion) + '_' + str(
                    annee) + '" SET "' + cours + '" = %s WHERE matricule = %s and annee = %s and session =%s',
                               [somme, matr, annee, session])

            ##################################################----------------------------session
            cursor.execute('SELECT * FROM "' + str(promotion) + '_' + str(
                annee) + '" WHERE matricule = %s and annee = %s and session =%s', [matr, annee,session])

            if cursor.rowcount >= 1:
                cmp= nbrcours+4

                varvide = 0
                vargrave = 0
                varleger = 0
                tot=float(0)
                records = cursor.fetchall()
                columns = cursor.description
                i=4
                while i<cmp:
                    if records[0][i] is None:
                        varvide += 0
                    else:
                        ponderationcours=enseigne.objects.filter(promotion_id=promotion,cours_id=int(columns[i][0]),annee_id=annee).aggregate(somme=Sum('ponderaton')).get('somme')

                        if ponderationcours is None:
                            ponderationcours=0
                        tot += float(records[0][i]) * float(ponderationcours)
                        if float(records[0][i]) >= 0 and float(records[0][i]) <= 7.9:
                            vargrave += 1
                        elif float(records[0][i]) >= 8 and float(records[0][i]) <= 10:
                            varleger += 1

                    i+=1

                pourc = float(tot * 100) / float(totponde)
                mention = mentionFinal(pourc, varleger, vargrave, varvide)
                cursor.execute('update "' + str(promotion) + '_' + str(annee) + '" set pourc=%s,nbrechec=%s,nbrechecleger=%s,nbrechecgrave=%s,nbrevide=%s,mention=%s where matricule=%s and session=%s and annee=%s',[ pourc, (varleger + vargrave), varleger, vargrave, varvide, mention,matr, session, annee])

                return True
            else:
                pourc = float(totGen * 100) / float(totponde)
                varvide = nbrcours-1
                vargrave = 0
                varleger = 0

                if somme >= 0 and somme <= 7.9:
                    vargrave += 1
                elif somme >= 8 and somme <= 10:
                    varleger += 1

                mention = mentionFinal(pourc, varleger, vargrave, varvide)

                cursor.execute('insert into "' + str(promotion) + '_' + str(annee) + '" (matricule,session,annee,pourc,nbrechec,nbrechecleger,nbrechecgrave,nbrevide,mention,"' + str(cours) + '") values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[matr,session,annee,pourc,(varleger + vargrave),varleger,vargrave,varvide,mention,somme])

                if session==2:#1er-session
                    cursor.execute('SELECT * FROM "' + str(promotion) + '_' + str(
                        annee) + '" WHERE matricule = %s and annee = %s and session =%s', [matr, annee, 1])
                    if cursor.rowcount >= 1:#ramener les item du mi-session
                        cmp = nbrcours + 4
                        records = cursor.fetchall()
                        columns = cursor.description
                        i = 4
                        while i < cmp:
                            if str(columns[0][i])!=str(cours):
                                cursor.execute('update "' + str(promotion) + '_' + str(
                                    annee) + ' set "' + str(columns[0][i]) + '" =%s where matricule=%s and session=%s and annee=%s',
                                               [records[0][i],matr,
                                                session, annee])
                            i += 1

                        #modifier pourcentage

                        cursor.execute('SELECT * FROM "' + str(promotion) + '_' + str(
                            annee) + '" WHERE matricule = %s and annee = %s and session =%s', [matr, annee, session])
                        if cursor.rowcount >= 1:
                            cmp = nbrcours + 4

                            varvide = 0
                            vargrave = 0
                            varleger = 0
                            tot = float(0)
                            records = cursor.fetchall()
                            columns = cursor.description
                            i = 4
                            while i < cmp:
                                if records[0][i] is None:
                                    varvide += 0
                                else:
                                    ponderationcours = enseigne.objects.filter(promotion_id=promotion,
                                                                               cours_id=int(columns[i][0]),
                                                                               annee_id=annee).aggregate(
                                        somme=Sum('ponderaton')).get('somme')
                                    if ponderationcours is None:
                                        ponderationcours = 0
                                    tot += float(records[0][i]) * float(ponderationcours)
                                    if float(records[0][i]) >= 0 and float(records[0][i]) <= 7.9:
                                        vargrave += 1
                                    elif float(records[0][i]) >= 8 and float(records[0][i]) <= 10:
                                        varleger += 1
                                i += 1
                            pourc = float(tot * 100) / float(totponde)
                            mention = mentionFinal(pourc, varleger, vargrave, varvide)
                            cursor.execute('update "' + str(promotion) + '_' + str(
                                annee) + '" set pourc=%s,nbrechec=%s,nbrechecleger=%s,nbrechecgrave=%s,nbrevide=%s,mention=%s where matricule=%s and session=%s and annee=%s',
                                           [pourc, (varleger + vargrave), varleger, vargrave, varvide, mention, matr,
                                            session, annee])

                        #modifier pourcentage

                if session==3:#2eme-session
                    cursor.execute('SELECT * FROM "' + str(promotion) + '_' + str(
                        annee) + '" WHERE matricule = %s and annee = %s and session =%s', [matr, annee, 2])
                    if cursor.rowcount >= 1:#ramener les item du 1er session
                        cmp = nbrcours + 4
                        records = cursor.fetchall()
                        columns = cursor.description
                        i = 4
                        while i < cmp:
                            if str(columns[0][i])!=str(cours):
                                cursor.execute('update "' + str(promotion) + '_' + str(
                                    annee) + ' set "' + str(columns[0][i]) + '" =%s where matricule=%s and session=%s and annee=%s',
                                               [records[0][i],matr,
                                                session, annee])
                            i += 1

                        #modifier pourcentage

                        cursor.execute('SELECT * FROM "' + str(promotion) + '_' + str(
                            annee) + '" WHERE matricule = %s and annee = %s and session =%s', [matr, annee, session])
                        if cursor.rowcount >= 1:
                            cmp = nbrcours + 4

                            varvide = 0
                            vargrave = 0
                            varleger = 0
                            tot = float(0)
                            records = cursor.fetchall()
                            columns = cursor.description
                            i = 4
                            while i < cmp:
                                if records[0][i] is None:
                                    varvide += 0
                                else:
                                    ponderationcours = enseigne.objects.filter(promotion_id=promotion,
                                                                               cours_id=int(columns[i][0]),
                                                                               annee_id=annee).aggregate(
                                        somme=Sum('ponderaton')).get('somme')
                                    if ponderationcours is None:
                                        ponderationcours = 0
                                    tot += float(records[0][i]) * float(ponderationcours)
                                    if float(records[0][i]) >= 0 and float(records[0][i]) <= 7.9:
                                        vargrave += 1
                                    elif float(records[0][i]) >= 8 and float(records[0][i]) <= 10:
                                        varleger += 1
                                i += 1
                            pourc = float(tot * 100) / float(totponde)
                            mention = mentionFinal(pourc, varleger, vargrave, varvide)
                            cursor.execute('update "' + str(promotion) + '_' + str(
                                annee) + '" set pourc=%s,nbrechec=%s,nbrechecleger=%s,nbrechecgrave=%s,nbrevide=%s,mention=%s where matricule=%s and session=%s and annee=%s',
                                           [pourc, (varleger + vargrave), varleger, vargrave, varvide, mention, matr,
                                            session, annee])

                        #modifier pourcentage
            ##################################################----------------------------session




def getpoint(image):
    from imutils.perspective import four_point_transform
    from imutils import contours
    import numpy as np
    import argparse
    import imutils
    import cv2

    # Les lignes 28 à 31 analysent nos arguments en ligne de commande. Nous n'avons besoin ici que d'un seul commutateur, - image  , qui représente le chemin d'accès à l'image test de feuille à bulles d'entrée que nous allons évaluer pour l'exactitude.

    # La ligne 36 définit ensuite notre ANSWER_KEY  .

    # Comme le nom de la variable le suggère, ANSWER_KEY   fournit des mappages entiers des  numéros de question à l'  index de la bulle correcte.

    # Dans ce cas, une touche de  0 indique la  première question , tandis qu'une valeur de  1 indique  «B» comme réponse correcte (puisque  «B» est l'index  1  de la chaîne  «ABCDE» ). Comme deuxième exemple, considérons une clé de  1 qui correspond à une valeur de  4 , ce qui indiquerait que la réponse à la deuxième question est  «E» .

    # Par commodité, j’ai écrit l’ensemble du corrigé en clair, ici:

    # Question n ° 1: B
    # Question n ° 2:  E
    # Question n ° 3:  A
    # Question n ° 4:  D
    # Question n ° 5:  B
    # ap = argparse.ArgumentParser()
    # ap.add_argument("-i", "--image", required=True,
    # 	help="path to the input image")
    # args = vars(ap.parse_args())

    # define the answer key which maps the question number
    # to the correct answer
    # ANSWER_KEY = {0: 1}
    # ANSWER_KEY = {0: 1, 1: 4, 2: 0, 3: 3, 4: 1}

    # Sur la  ligne 41,  nous chargeons notre image à partir du disque, puis nous la convertissons en niveaux de gris ( ligne 42 ) et nous la rendons floue pour réduire le bruit haute fréquence ( ligne 43 ).

    # Nous appliquons ensuite le détecteur de bords Canny sur la  ligne 44 pour trouver les  contours / contours de l’examen.

    # image = cv2.imread(args["image"])
    # image = cv2.imread("testglodirote.jpg")
    # image = cv2.imread("Final.jpg")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    # Maintenant que nous avons les grandes lignes de notre examen, nous appliquons le CV2 . findContours   fonction permet de rechercher les lignes correspondant à l’examen lui-même.

    # Nous faisons cela en triant nos contours par leur  surface (du plus grand au plus petit) sur la  ligne 66 (après s’être assuré qu’au moins un contour a été trouvé sur la  ligne 63 , bien sûr). Cela implique que des contours plus grands seront placés au début de la liste, tandis que des contours plus petits apparaîtront plus loin dans la liste.

    # Nous supposons que notre examen sera le  point central de l'image et sera donc plus grand que les autres objets de l'image. Cette hypothèse nous permet de «filtrer» nos contours, simplement en recherchant leur zone et en sachant que le contour qui correspond à l'examen doit se situer près du début de la liste.

    # Cependant, la  surface et la taille du contour ne suffisent pas - nous devrions également vérifier le nombre de  sommets du contour.

    # Pour ce faire, nous passons en boucle sur chacun de nos contours (triés) sur la  ligne 69 . Pour chacun d'eux, nous approchons le contour, ce qui signifie essentiellement que nous  simplifions le nombre de points dans le contour, ce qui en fait une forme géométrique «plus fondamentale».

    # Sur la  ligne 79, nous vérifions si notre contour approximatif a quatre points et, le cas échéant,  nous supposons que nous avons trouvé l’examen.

    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    docCnt = None

    # ensure that at least one contour was found
    if len(cnts) > 0:
        # sort the contours according to their size in
        # descending order
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        # loop over the sorted contours
        for c in cnts:
            # approximate the contour
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            # if our approximated contour has four points,
            # then we can assume we have found the paper
            if len(approx) == 4:
                docCnt = approx
                break

    # Maintenant que nous avons utilisé des contours pour trouver le contour de l'examen, nous pouvons appliquer une transformation de perspective pour obtenir une vue de haut en bas du document:
    # Dans ce cas, nous utiliserons mon implémentation de la   fonction four_point_transform qui:

    # Ordonne les  coordonnées (x, y) de nos contours de manière  spécifique et reproductible.
    # Applique une transformation de perspective à la région.
    # mais pour le moment, sachez simplement que cette fonction prend en charge l'examen «asymétrique» et le transforme, ce qui permet d'obtenir une vue de haut en bas. le document:
    paper = four_point_transform(image, docCnt.reshape(4, 2))
    warped = four_point_transform(gray, docCnt.reshape(4, 2))

    # Cette étape commence par la  binarisation ou le processus de seuillage / segmentation du  premier plan à partir du  fond de l’image:
    # Après application de la méthode de seuillage d'Otsu, notre examen est maintenant une  image binaire :
    # Notez que l’ arrière -  plan  de l’image est  noir alors que l’  avant - plan est  blanc.
    # Cette binarisation nous permettra à nouveau d’appliquer des techniques d’extraction de contour pour trouver chacune des bulles de l’examen:
    thresh = cv2.threshold(warped, 0, 255,
                           cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    # Les lignes 106 à 109 gèrent la recherche des contours sur notre   image binaire de battement , suivies de l’initialisation de questionCnts  , une liste de contours correspondant aux questions / bulles de l’examen.

    # Pour déterminer quelles régions de l’image sont des bulles, on passe d’abord en boucle sur chacun des contours individuels ( Ligne 112 ).
    # Pour chacun de ces contours, nous calculons le cadre de sélection ( ligne 114 ), ce qui nous permet également de calculer le rapport de format , ou plus simplement, le rapport entre la largeur et la hauteur ( ligne 115 ).

    # Pour qu'une zone de contour soit considérée comme une bulle, la région doit:

    # Être suffisamment large et haut (dans ce cas, au moins 20 pixels dans les deux dimensions).
    # Avoir un rapport d'aspect qui est approximativement égal à 1.
    # Tant que ces vérifications sont vérifiées, nous pouvons mettre à jour notre   liste questionCnts et marquer la région comme une bulle.
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    questionCnts = []

    # loop over the contours
    for c in cnts:
        # compute the bounding box of the contour, then use the
        # bounding box to derive the aspect ratio
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)

        # in order to label the contour as a question, region
        # should be sufficiently wide, sufficiently tall, and
        # have an aspect ratio approximately equal to 1
        if w >= 20 and h >= 20 and ar >= 0.9 and ar <= 1.1:
            questionCnts.append(c)

    # Nous pouvons maintenant passer à la partie «classement» de notre système de RMP:
    # Premièrement, nous devons trier nos questions   de fond en comble. Cela garantira que les rangées de questions  plus proches du début de l'examen apparaîtront en premier dans la liste triée.
    # Nous initialisons également une variable comptable pour garder une trace du nombre de   réponses correctes .

    questionCnts = contours.sort_contours(questionCnts,
                                          method="top-to-bottom")[0]
    correct = 0
    seuil = 300
    Cmptseuil = 0
    CmptNote = 11  # 11 ppour la note 2 pour qrcode ki est exclu
    CmptNoteD = 10  # 0-10 ppour la note 2 pour qrcode ki est exclu
    bubbled = None

    # Sur la  ligne 148, nous commençons à boucler nos questions. Étant donné que chaque question a 5 réponses possibles, nous appliquerons le découpage en tableau et le tri de contours NumPy pour trier le  jeu de contours actuel de gauche à droite.
    # Cette méthodologie fonctionne parce que nous avons  déjà trié nos contours de haut en bas. Nous  savons que les 5 bulles de chaque question apparaîtront de manière séquentielle dans notre liste -  mais nous  ne savons pas  si ces bulles seront triées de gauche à droite.
    # L’appel du contour sur la  ligne 152 règle ce problème et garantit que chaque ligne de contour est triée en lignes, de gauche à droite.

    # A partir d’une rangée de bulles, l’étape suivante consiste à déterminer quelle bulle est remplie.

    # Nous pouvons accomplir cela en utilisant notre
    # image thresh et en comptant le nombre de pixels
    # non nuls (c'est-à-dire les  pixels au premier plan )
    # 	dans chaque zone de bulle:

    # print(len(questionCnts))
    for (q, i) in enumerate(np.arange(0, len(questionCnts), 1)):

        # sort the contours for the current question from
        # left to right, then initialize the index of the
        # bubbled answer
        cnts = contours.sort_contours(questionCnts[i:i + 1])[0]

        # A partir d’une rangée de bulles, l’étape suivante consiste à déterminer quelle bulle est remplie.

        #    Nous pouvons accomplir cela en utilisant notre
        #    image thresh et en comptant le nombre de pixels
        #    non nuls (c'est-à-dire les  pixels au premier plan ) dans chaque zone de bulle:
        # 	La ligne 168 gère la mise en boucle sur chacune des bulles triées de la rangée.

        # Nous construisons ensuite un masque pour la bulle actuelle sur la  ligne 171 ,
        # puis comptons le nombre de pixels non nuls dans la région masquée ( lignes 177 et 178 ).
        # Plus nous comptons de pixels non nuls, plus le nombre de pixels d’avant-plan est important.
        # Par conséquent, la bulle avec le nombre maximal non nul est l’indice de la bulle dans laquelle
        # le preneur d’essai a fait des bulles ( Lignes 183 et 184 ).
        for (j, c) in enumerate(cnts):
            # construct a mask that reveals only the current
            # "bubble" for the question
            mask = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)

            # apply the mask to the thresholded image, then
            # count the number of non-zero pixels in the
            # bubble area
            mask = cv2.bitwise_and(thresh, thresh, mask=mask)
            total = cv2.countNonZero(mask)

            # if the current total has a larger number of total
            # non-zero pixels, then we are examining the currently
            # bubbled-in answer
            # if CmptNoteD !=12:
            # 		if CmptNoteD !=11:
            #print(CmptNoteD, total)
            if total >= seuil:  # verifier si le seuil est superieur ou egal à 400
                Cmptseuil += 1  # compteur pour voir si ya plusieur bulle cocher

            if bubbled is None or total > bubbled[0]:
                bubbled = (total, CmptNoteD)

        CmptNoteD -= 1

    # print(bubbled)

    if len(questionCnts) == CmptNote:  # verifier si les bulles de notes sont a 13

        if Cmptseuil == 0:  # aucun bulle cocher
            return -2
        elif Cmptseuil == 1:  # one bulle cocher
            return bubbled[1]
        else:  # plusieurs bulle cocher
            return -3


    else:  # les bulles ne sont pas 13
        return -1



def rotate_image(mat, angle):
    """
    Rotates an image (angle in degrees) and expands image to avoid cropping
    """
    import cv2

    height, width = mat.shape[:2] # image shape has 3 dimensions
    image_center = (width/2, height/2) # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape

    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

    # rotation calculates the cos and sin, taking absolutes of those.
    abs_cos = abs(rotation_mat[0,0])
    abs_sin = abs(rotation_mat[0,1])

    # find the new width and height bounds
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    # subtract old image center (bringing image back to origo) and adding the new image center coordinates
    rotation_mat[0, 2] += bound_w/2 - image_center[0]
    rotation_mat[1, 2] += bound_h/2 - image_center[1]


    # rotate image with the new bounds and translated rotation matrix
    rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h),borderMode=cv2.BORDER_CONSTANT,
                           borderValue=(0,255,0))

    #rotated_mat = cv2.warpAffine(mat, rotation_mat, (390, 468))
    return rotated_mat



class ExemplaireBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
    model = exemplaire
    fields = '__all__'
    raise_exception = True
    success_url = reverse_lazy('cote:exemplaire')

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
        form = super(ExemplaireBaseView, self).get_form(*args, **kwargs)
        [self._formatcss(form, f) for f in form.fields]
        # self._formatcssdate(form, ["date_naissance"])
        # self._formatcssnonrequired(form, ["observation"])
        return form
    def get_success_url(self):
        if '_continue' in self.request.POST:
            url = reverse_lazy('cote:exemplaire_update', kwargs={'pk': self.object.pk}, )
        elif '_addanother' in self.request.POST:
            url = reverse_lazy('cote:exemplaire_create')
        else:
            url = reverse_lazy('cote:exemplaire')
        return url
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["annee"] = annee.objects.filter(etat=True)
        context["departement"] = departements.objects.filter(etat=True)
        # context["cours"] = cours.objects.all()

        # calculerpourcentage(1,1,18,4,"45545")
        
        return context

class ExemplaireListView(ExemplaireBaseView, ListView):

    def get(self, request, *args, **kwargs):
        if 'courspro' in request.GET:
            if request.GET.get('promotion')=='':
                return JsonResponse({'data': []}, safe=False)
            courslist = enseigne.objects.filter(promotion_id=request.GET.get('promotion'),
                                              annee_id=request.GET.get('annee')
                                              ).values(
                'cours__libelle',
                'cours__sigle',
                'cours_id',
            ).order_by("cours__libelle", "cours_id")

            data=list(courslist)
            return JsonResponse({'data': data}, safe=False)
        if 'epreuve' in request.GET:
            if request.GET.get('cours')=='':
                return JsonResponse({'data': []}, safe=False)
            data = exemplaire.objects.filter(promotion_id=request.GET.get('promotion'),
                                           annee_id=request.GET.get('annee'),
                                           cours_id=request.GET.get('cours'),
                                           sesionn=request.GET.get('epreuve'),
                                           numero=request.GET.get('numero'),
                                           ).values(

                'matricule_id',
                'matricule__matricule',
                'matricule__nom',
                'matricule__postnom',
                'matricule__prenom',
                'lien',
                'matricule__sexe',
                'matricule__telephone'
            )
            data = list(data)
            return JsonResponse({'data': data}, safe=False)

        return super(ExemplaireListView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if 'impression' in request.POST:
            ex = exemplaire.objects.filter(
                promotion_id=request.POST.get("promotion"),
                annee_id=request.POST.get("annee"),
                cours_id=request.POST.get("cours"),
                sesionn=request.POST.get("epreuve"),
                numero=request.POST.get("numero")
            )
            if ex:
                fn = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                ex=ex.first().lien
                input_file = os.path.join(fn, 'media')
                input_file = os.path.join(input_file, str(ex))
                for file in os.listdir(input_file):
                    file_name = os.path.join(input_file, file)
                    if os.path.isfile(file_name):
                        os.startfile(file_name, "print")
                return HttpResponse('true')


        elif 'epreuve' in request.POST :
            from cryptography.fernet import Fernet
            f = Fernet("ZmDfcHP8_60GrrY767zsiPd62pEvs0aGOv0oasOM1Pg=")

            e = etudprom.objects.filter(promotion_id=request.POST.get("promotion"), annee_id=request.POST.get("annee"))
            for i in e:
                fn = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                input_file = os.path.join(fn, 'exemplaire.jrxml')
                output_file = os.path.join(fn, 'media')
                lientxt=str(request.POST.get("anneelib"))+"/"+str(request.POST.get("promotionlib"))+"/"+str(request.POST.get("courslib"))+"/"+str(request.POST.get("epreuvelib"))+"/"+str(request.POST.get("numero"))+"/"
                annee = os.path.join(output_file, str(request.POST.get("anneelib")))
                promotion = os.path.join(annee, str(request.POST.get("promotionlib")))
                cours = os.path.join(promotion, str(request.POST.get("courslib")))
                epreuve = os.path.join(cours, str(request.POST.get("epreuvelib")))
                numero = os.path.join(epreuve, str(request.POST.get("numero")))
                matr = f.encrypt(str(str(i.matricule.matricule)+'~'+str(request.POST.get("promotion"))+'~'+str(request.POST.get("cours"))+'~'+str(request.POST.get("epreuve"))+'~'+str(request.POST.get("numero"))+'~'+str(request.POST.get("annee"))).encode())#matr promotion cours session numero annee
                if os.path.isdir(annee):
                    if os.path.isdir(promotion):
                        if os.path.isdir(cours):
                            if os.path.isdir(epreuve):
                                if os.path.isdir(numero):
                                    pass
                                else:
                                    os.makedirs(numero)
                            else:
                                os.makedirs(epreuve)
                                os.makedirs(numero)
                        else:
                            os.makedirs(cours)
                            os.makedirs(epreuve)
                            os.makedirs(numero)
                    else:
                        os.makedirs(promotion)
                        os.makedirs(cours)
                        os.makedirs(epreuve)
                        os.makedirs(numero)
                else:
                    os.makedirs(annee)
                    os.makedirs(promotion)
                    os.makedirs(cours)
                    os.makedirs(epreuve)
                    os.makedirs(numero)

                matr_link=re.sub(r"\D", "", str(i.matricule.matricule))
                output_file = os.path.join(numero, str(matr_link))
                if os.path.isdir(output_file):
                    pass
                else:

                    con = {
                        'driver': 'generic',
                        'jdbc_driver': 'org.postgresql.Driver',
                        'jdbc_url': 'jdbc:postgresql://localhost:5432/' + str(settings.DATABASES['default']['NAME']),
                        'jdbc_dir': fn,
                        'username': settings.DATABASES['default']['USER'],
                        'password': settings.DATABASES['default']['PASSWORD'],

                    }
                    epreuve = str(request.POST.get("epreuvelib")).split('SESSION')
                    if len(epreuve) > 1:
                        epreuve = "Examen"
                        nepreuve = request.POST.get("epreuvelib")
                    else:
                        epreuve = request.POST.get("epreuvelib")
                        nepreuve = 'N° '+str(request.POST.get("numero"))

                    jasper = JasperPy()
                    jasper.process(
                        input_file,
                        output_file,
                        format_list=["pdf"],
                        db_connection=con,
                        parameters={'n': nepreuve,
                                    'annee': request.POST.get("annee"),
                                    'anneelib': request.POST.get("anneelib"),
                                    'anonymat': request.POST.get("anonymat"),
                                    'epreuve': epreuve,
                                    'matricule': str(i.matricule.matricule),
                                    'matrx': matr.decode('utf-8'),
                                    'promotion': request.POST.get("promotion"),
                                    'cours': request.POST.get("courslib")
                                    },
                        locale='en_US'
                    )

                    ex = exemplaire.objects.filter(
                        matricule_id=i.matricule.id,
                        promotion_id=request.POST.get("promotion"),
                        annee_id=request.POST.get("annee"),
                        cours_id=request.POST.get("cours"),
                        sesionn=request.POST.get("epreuve"),
                        numero=request.POST.get("numero")
                    )
                    if ex:
                        pass
                    else:
                        exemplaire.objects.create(
                            user=request.user,
                            numero=request.POST.get("numero"),
                            lien=lientxt,
                            matricule_id=i.matricule.id,
                            promotion_id=request.POST.get("promotion"),
                            annee_id=request.POST.get("annee"),
                            cours_id=request.POST.get("cours"),
                            sesionn=request.POST.get("epreuve"),
                        )

                    # encrypting
                    # from cryptography.fernet import Fernet
                    # f = Fernet("ZmDfcHP8_60GrrY767zsiPd62pEvs0aGOv0oasOM1Pg=")
                    # message = "1245.2415".encode()
                    #
                    # encrypted = f.encrypt(message)
                    # decrypted = f.decrypt(encrypted)
                    #
                    # print(encrypted)
                    # print(decrypted)
            return HttpResponse('true')


        return super(ExemplaireListView, self).post(request, *args, **kwargs)
class ExemplaireDetailView(ExemplaireBaseView, DetailView):
    pass
class ExemplaireCreateView(ExemplaireBaseView, CreateView):
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object = form.save()
        etudprom.objects.create(
            matricule_id=self.object.id,
            promotion_id=self.request.POST.get("promotion"),
            annee_id=self.request.POST.get("annee"))
        return super().form_valid(form)
class ExemplaireUpdateView(ExemplaireBaseView, UpdateView):

    # def form_valid(self, form):
    #     self.object = form.save(commit=False)
    #     self.object.user = self.request.user
    #     self.object = form.save()
    #     etudprom.objects.create(
    #         matricule_id=self.object.id,
    #         promotion_id=self.request.POST.get("promotion"),
    #         annee_id=self.request.POST.get("annee"))
    #     return super().form_valid(form)

    # def get_context_data(self, **kwargs):
    #     context = super(EtudiantsBaseView, self).get_context_data(**kwargs)
    #     # data = etudprom.objects.filter(matricule_id=self.kwargs['pk']).order_by('-id').first()
    #     # context['promotionid'] = data.promotion.id
    #     # context['anneeid'] = data.annee.id
    #     context['update'] = 1
    #
    #     return context
    pass
class ExemplaireDeleteView(ExemplaireBaseView, DeleteView):
    pass



@login_required
@permission_required('cote.deliberation')
def deliberation(request):

    context={
        'promotion':promotions.objects.all(),
        'annee':annee.objects.all(),
    }
    return render(request,'cote/deliberation.html',context)

@login_required
@permission_required('cote.deliberation')
def listdeliberation(request):

        dt=[]
        dtmatricule=[]

        with connection.cursor() as cursor:
            try:
                cursor.execute('SELECT e.matricule_id,nom,postnom,pourc as pourcentage,mention,nbrechec,nbrechecleger,nbrechecgrave,nbrevide FROM "' + str(request.GET.get('promotion')) + '_' + str(
                    request.GET.get('annee')) + '" inner join parametrage_etudiants on parametrage_etudiants.id::varchar(255)="' + str(request.GET.get('promotion')) + '_' + str(
                    request.GET.get('annee')) + '".matricule inner join cote_etudprom as e on parametrage_etudiants.id=e.matricule_id WHERE annee = %s and session =%s order by nom', [str(request.GET.get('annee')),request.GET.get('epreuve')])
                if cursor.rowcount >= 1:
                    for i in cursor.fetchall():
                        dtmatricule.append(i[0])
                        dt.append(
                            {
                                "matricule_id":i[0],
                                "nom":i[1],
                                "postnom":i[2],
                                "pourcentage":i[3],
                                "mention":i[4],
                                "nbrechec":i[5],
                                "nbrechecleger":i[6],
                                "nbrechecgrave":i[7],
                                "nbrevide":i[8]

                             }
                        )
            except:
                pass


        clist = etudprom.objects.filter(promotion_id=request.GET.get('promotion'),
                                          annee_id=request.GET.get('annee')
                                          ).exclude(matricule_id__in=dtmatricule).annotate(
        pourcentage=Value('', output_field=CharField()),
        mention=Value('', output_field=CharField()),
        nbrechec=Value('', output_field=CharField()),
        nbrechecleger=Value('', output_field=CharField()),
        nbrechecgrave=Value('', output_field=CharField()),
        nbrevide=Value('', output_field=CharField()),
            nom=F('matricule__nom'),
            postnom=F('matricule__postnom'),
            ).values(
            'matricule_id',
            'nom',
            'postnom',
            'pourcentage',
            'mention',
            'nbrechec',
            'nbrechecleger',
            'nbrechecgrave',
            'nbrevide'
        ).order_by("nom")
        dt.extend(list(clist))

        return JsonResponse({'data': dt}, safe=False)


@login_required
@permission_required('cote.deliberation')
def listdeliberationone(request):

        # dt=[]
        # with connection.cursor() as cursor:
        #     try:
        #         cursor.execute('SELECT e.matricule_id,nom,postnom,pourc as pourcentage,mention,nbrechec,nbrechecleger,nbrechecgrave,nbrevide FROM "' + str(request.GET.get('promotion')) + '_' + str(
        #             request.GET.get('annee')) + '" inner join parametrage_etudiants on parametrage_etudiants.id::varchar(255)="' + str(request.GET.get('promotion')) + '_' + str(
        #             request.GET.get('annee')) + '".matricule inner join cote_etudprom as e on parametrage_etudiants.id=e.matricule_id WHERE annee = %s and session =%s and e.matricule_id=%s order by nom', [str(request.GET.get('annee')),request.GET.get('epreuve'),request.GET.get('matricule')])
        #         if cursor.rowcount >= 1:
        #             for i in cursor.fetchall():
        #                 dt.append(
        #                     {
        #                         "matricule_id":i[0],
        #                         "nom":i[1],
        #                         "postnom":i[2],
        #                         "pourcentage":i[3],
        #                         "mention":i[4],
        #                         "nbrechec":i[5],
        #                         "nbrechecleger":i[6],
        #                         "nbrechecgrave":i[7],
        #                         "nbrevide":i[8]
        #
        #                      }
        #                 )
        #     except:
        #         pass
        data = cote.objects.filter(promotion_id=request.GET.get('promotion'),
                                   annee_id=request.GET.get('annee'),
                                   sesionn=request.GET.get('epreuve'),
                                   matricule_id=request.GET.get('matricule'),
                                   numero=request.GET.get('numero'),
                                   ).values(

            'id',
            'cours__sigle',
            'cours_id',
            'cours__enseigne__categorie',
            'sesionn',
            'cote',
            'lien',
        ).order_by('cours__enseigne__categorie')


        return JsonResponse({'data': list(data)}, safe=False)


class CoteBaseView(LoginRequiredMixin,PermissionRequiredMixin,View):
    model = cote
    fields = '__all__'
    raise_exception = True
    success_url = reverse_lazy('cote:cote')

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
        form = super(CoteBaseView, self).get_form(*args, **kwargs)
        [self._formatcss(form, f) for f in form.fields]
        # self._formatcssdate(form, ["date_naissance"])
        # self._formatcssnonrequired(form, ["observation"])
        return form
    def get_success_url(self):
        if '_continue' in self.request.POST:
            url = reverse_lazy('cote:cote_update', kwargs={'pk': self.object.pk}, )
        elif '_addanother' in self.request.POST:
            url = reverse_lazy('cote:cote_create')
        else:
            url = reverse_lazy('cote:cote')
        return url
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["annee"] = annee.objects.all()
        context["promotion"] = promotions.objects.all()
        #context["cours"] = cours.objects.all()
        
        return context

class CoteListView(CoteBaseView, ListView):

    def get(self, request, *args, **kwargs):
        if 'simple' in request.GET :

            data = cote.objects.filter(promotion_id=request.GET.get('promotion'),
                                           annee_id=request.GET.get('annee'),
                                           cours_id=request.GET.get('cours'),
                                           sesionn=request.GET.get('epreuve'),
                                           numero=request.GET.get('numero'),
                                           ).values(

                'matricule_id',
                'matricule__matricule',
                'matricule__nom',
                'matricule__postnom',
                'matricule__prenom',
                'cote',
                'lien',
            )
            data2 = etudprom.objects.filter(promotion_id=request.GET.get('promotion'),
                                       annee_id=request.GET.get('annee')

                                       ).exclude(matricule_id__in=data.values('matricule_id')).annotate(
        cote=Value('', output_field=CharField()),
        lien=Value('', output_field=CharField())
            ).values(

                        'matricule_id',
                        'matricule__matricule',
                        'matricule__nom',
                        'matricule__postnom',
                        'matricule__prenom',
                        'cote',
                        'lien',
                    )
            data = list(data)
            data2 = list(data2)
            data.extend(data2)
            return JsonResponse({'data': data}, safe=False)
        if 'compose' in request.GET :

            datalist=[]
            cotesession = cote.objects.filter(promotion_id=request.GET.get('promotion'),
                                           annee_id=request.GET.get('annee'),
                                           cours_id=request.GET.get('cours'),
                                           sesionn__in=('1','2','3'),#mi-sessoon,1er session,2ieme session
                                           numero=request.GET.get('numero'),
                                           ).values(

                'matricule_id',
                'matricule__matricule',
                'matricule__nom',
                'matricule__postnom',
                'matricule__prenom',
                'cote',
                'sesionn',
                'lien',
            ).annotate(cote1=Sum("cote")).order_by("matricule_id","sesionn")
            matr =0

            for i in cotesession:
                tst = {}
                if matr!=i["matricule_id"]:
                    tst["matricule_id"]=i["matricule_id"]
                    tst["matricule__matricule"]=i["matricule__matricule"]
                    tst["matricule__nom"]=i["matricule__nom"]
                    tst["matricule__postnom"]=i["matricule__postnom"]
                    tst["matricule__prenom"]=i["matricule__prenom"]
                    tst["lien"]=i["lien"]
                    tst["cote1"] = i["cote1"]
                    tst["cote2"]=""
                    tst["cote3"]=""
                    if i["sesionn"]=="1":
                        tst["session1"] = i["sesionn"]
                    elif i["sesionn"]=="2":
                        tst["session2"]=i["sesionn"]
                    elif i["sesionn"]=="3":
                        tst["session3"]=i["sesionn"]
                    matr = i["matricule_id"]
                    datalist.append(tst)
                else:
                    if i["sesionn"]=="2":
                        datalist[len(datalist)-1]['cote2']=i["cote1"]
                    elif i["sesionn"]=="3":
                        datalist[len(datalist)-1]['cote3']=i["cote1"]




            data2 = etudprom.objects.filter(promotion_id=request.GET.get('promotion'),
                                       annee_id=request.GET.get('annee')

                                       ).exclude(matricule_id__in=cotesession.values('matricule_id')).annotate(
        cote1=Value('', output_field=CharField()),
        cote2=Value('', output_field=CharField()),
        cote3=Value('', output_field=CharField()),
        sesionn=Value(0, output_field=FloatField()),
        lien=Value('', output_field=CharField())
            ).values(

                        'matricule_id',
                        'matricule__matricule',
                        'matricule__nom',
                        'matricule__postnom',
                        'matricule__prenom',
                        'lien',
                        'sesionn',
                'cote1',
                'cote2',
                'cote3',
                    )


            data2 = list(data2)
            datalist.extend(data2)
            return JsonResponse({'data': datalist}, safe=False)
        if 'compose2' in request.GET :
            datalist=[]
            cotesession = cote.objects.filter(promotion_id=request.GET.get('promotion'),
                                           annee_id=request.GET.get('annee'),
                                           matricule_id=request.GET.get('matricule'),
                                           sesionn__in=('1','2','3'),#mi-sessoon,1er session,2ieme session
                                           numero=request.GET.get('numero'),
                                           ).values(


                'cours__libelle',
                'cours__sigle',
                'cours_id',
                'cote',
                'sesionn',
                'lien',
            ).annotate(cote1=Sum("cote")).order_by("cours_id","sesionn")
            coursx =0

            for i in cotesession:
                tst = {}
                if coursx!=i["cours_id"]:
                    tst["cours_id"]=i["cours_id"]
                    tst["cours__libelle"]=i["cours__libelle"]
                    tst["cours__sigle"]=i["cours__sigle"]
                    tst["lien"]=i["lien"]
                    tst["cote1"] = i["cote1"]
                    tst["cote2"]=""
                    tst["cote3"]=""
                    if i["sesionn"]=="1":
                        tst["session1"] = i["sesionn"]
                    elif i["sesionn"]=="2":
                        tst["session2"]=i["sesionn"]
                    elif i["sesionn"]=="3":
                        tst["session3"]=i["sesionn"]
                    coursx = i["cours_id"]
                    datalist.append(tst)
                else:
                    if i["sesionn"]=="2":
                        datalist[len(datalist)-1]['cote2']=i["cote1"]
                    elif i["sesionn"]=="3":
                        datalist[len(datalist)-1]['cote3']=i["cote1"]




            data2 = enseigne.objects.filter(promotion_id=request.GET.get('promotion'),
                                       annee_id=request.GET.get('annee')

                                       ).exclude(cours_id__in=cotesession.values('cours_id')).annotate(
        cote1=Value('', output_field=CharField()),
        cote2=Value('', output_field=CharField()),
        cote3=Value('', output_field=CharField()),
        sesionn=Value(0, output_field=FloatField()),
        lien=Value('', output_field=CharField())
            ).values(


                         'cours__libelle',
                'cours__sigle',
                'cours_id',
                        'lien',
                        'sesionn',
                'cote1',
                'cote2',
                'cote3',
                    )


            data2 = list(data2)
            datalist.extend(data2)
            return JsonResponse({'data': datalist}, safe=False)
        if 'getchange' in request.GET:

            if request.GET.get('categorie')=='1':
                courslist = enseigne.objects.filter(promotion_id=request.GET.get('promotion'),
                                                  annee_id=request.GET.get('annee')
                                                  ).values(
                    'cours__libelle',
                    'cours_id',
                ).order_by("cours__libelle", "cours_id")

                data=list(courslist)
                return JsonResponse({'data': data}, safe=False)
            elif request.GET.get('categorie')=='2':
                courslist = etudprom.objects.filter(promotion_id=request.GET.get('promotion'),
                                                    annee_id=request.GET.get('annee')
                                                    ).annotate(
        cours__libelle=F('matricule__nom'),
        cours_id=F('matricule_id')
            ).values('cours__libelle','cours_id').order_by("cours__libelle", "cours_id")

                data = list(courslist)
                return JsonResponse({'data': data}, safe=False)
        if 'courspro' in request.GET:

            courslist = enseigne.objects.filter(promotion_id=request.GET.get('promotion'),
                                              annee_id=request.GET.get('annee')
                                              ).values(
                'cours__libelle',
                'cours_id',
            ).order_by("cours__libelle", "cours_id")

            data=list(courslist)
            return JsonResponse({'data': data}, safe=False)


        return super(CoteListView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        try:
            c = cote.objects.filter(
                matricule_id=request.POST.get("matricule"),
                cours_id=request.POST.get("cours"),
                sesionn=request.POST.get("epreuve"),
                numero=request.POST.get("numero"),
                promotion_id=request.POST.get("promotion"),
                annee_id=request.POST.get("annee"))
            if c:
                if request.user.has_perm("cote.change_cote"):

                    c.update(
                        user=request.user,
                        cote=float(request.POST.get("cote")))
                    calculerpourcentage(request.POST.get("annee"),
                                        request.POST.get("promotion"),
                                        request.POST.get("cours"),
                                        request.POST.get("epreuve"), request.POST.get("matricule"))
                    return JsonResponse({'msg': "Opération effectuee", 'id': "1"}, safe=False)
                else:
                    return JsonResponse({'msg': "Utilisateur n'a pas le droit de modifier",'id':"0"}, safe=False)

            else:

                if request.user.has_perm("cote.add_cote"):
                    cote.objects.create(
                        matricule_id=request.POST.get("matricule"),
                        cours_id=request.POST.get("cours"),
                        sesionn=request.POST.get("epreuve"),
                        numero=request.POST.get("numero"),
                        user=request.user,
                        cote=float(request.POST.get("cote")),
                        promotion_id=request.POST.get("promotion"),
                        annee_id=request.POST.get("annee"))
                    calculerpourcentage(request.POST.get("annee"),
                                        request.POST.get("promotion"),
                                        request.POST.get("cours"),
                                        request.POST.get("epreuve"), request.POST.get("matricule"))
                    return JsonResponse({'msg': "Opération effectuee", 'id': "1"}, safe=False)
                else:
                    return JsonResponse({'msg': "Utilisateur n'a pas le droit d'aujout",'id':"0"}, safe=False)
        except Exception as e:
            return JsonResponse({'msg': str(e),'id':"0"}, safe=False)
# class CoteDetailView(CoteBaseView, DetailView):
#     pass
# class CoteCreateView(CoteBaseView, CreateView):
#     def form_valid(self, form):
#         self.object = form.save(commit=False)
#         self.object.user = self.request.user
#         self.object = form.save()
#         etudprom.objects.create(
#             matricule_id=self.object.id,
#             promotion_id=self.request.POST.get("promotion"),
#             annee_id=self.request.POST.get("annee"))
#         return super().form_valid(form)
# class CoteUpdateView(CoteBaseView, UpdateView):
#
#     # def form_valid(self, form):
#     #     self.object = form.save(commit=False)
#     #     self.object.user = self.request.user
#     #     self.object = form.save()
#     #     etudprom.objects.create(
#     #         matricule_id=self.object.id,
#     #         promotion_id=self.request.POST.get("promotion"),
#     #         annee_id=self.request.POST.get("annee"))
#     #     return super().form_valid(form)
#
#     # def get_context_data(self, **kwargs):
#     #     context = super(EtudiantsBaseView, self).get_context_data(**kwargs)
#     #     # data = etudprom.objects.filter(matricule_id=self.kwargs['pk']).order_by('-id').first()
#     #     # context['promotionid'] = data.promotion.id
#     #     # context['anneeid'] = data.annee.id
#     #     context['update'] = 1
#     #
#     #     return context
#     pass
# class CoteDeleteView(CoteBaseView, DeleteView):
#     pass



#@csrf_exempt
@require_POST
@login_required
def addfile(request):
    import cv2
    import numpy
    from cryptography.fernet import Fernet
    fcryp = Fernet("ZmDfcHP8_60GrrY767zsiPd62pEvs0aGOv0oasOM1Pg=")

    fn = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(fn, 'media')
    annee = os.path.join(output_file, str(request.POST.get("anneelib")))
    promotion = os.path.join(annee, str(request.POST.get("promotionlib")))
    cours = os.path.join(promotion, str(request.POST.get("courslib")))
    epreuve = os.path.join(cours, str(request.POST.get("epreuvelib")))
    numero = os.path.join(epreuve, str(request.POST.get("numero")))
    corrige = os.path.join(numero, "corrige")
    # matr = f.encrypt(str(i.matricule.matricule).encode())  # matr promotion cours session numero annee
    if os.path.isdir(annee):
        if os.path.isdir(promotion):
            if os.path.isdir(cours):
                if os.path.isdir(epreuve):
                    if os.path.isdir(numero):
                        if os.path.isdir(corrige):
                            pass
                        else:
                            os.makedirs(corrige)

                        ###################################################logique

                        for f in request.FILES.getlist('file'):
                            ############################################################recuperer qrcode
                            image = cv2.imdecode(numpy.fromstring(f.read(), numpy.uint8),
                                                 cv2.IMREAD_UNCHANGED)
                            qrCodeDetector = cv2.QRCodeDetector()
                            decodedText, points, straight_qrcode = qrCodeDetector.detectAndDecode(image)
                            if points is not None:
                                decrypted = fcryp.decrypt(str(decodedText).encode()).decode()
                                corrigecopie = os.path.join(corrige, str(decrypted) + ".jpg")
                                if os.path.exists(corrigecopie):
                                    pass
                                else:
                                    fs = FileSystemStorage()
                                    fs.save(corrigecopie, f)
                            else:
                                print("QR code not detected")
                            ############################################################recuperer qrcode

                        ###################################################logique
                        return HttpResponse()
    return HttpResponseForbidden()



@require_POST
@login_required
def corriger(request):
    import cv2
    from cryptography.fernet import Fernet
    fcryp = Fernet("ZmDfcHP8_60GrrY767zsiPd62pEvs0aGOv0oasOM1Pg=")

    fn = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(fn, 'media')
    staticlink = os.path.join(fn, 'static')
    lientxt = str(request.POST.get("anneelib")) + "/" + str(request.POST.get("promotionlib")) + "/" + str(
        request.POST.get("courslib")) + "/" + str(request.POST.get("epreuvelib")) + "/" + str(request.POST.get("numero")) + "/corrige/"

    annee = os.path.join(output_file, str(request.POST.get("anneelib")))
    promotion = os.path.join(annee, str(request.POST.get("promotionlib")))
    cours = os.path.join(promotion, str(request.POST.get("courslib")))
    epreuve = os.path.join(cours, str(request.POST.get("epreuvelib")))
    numero = os.path.join(epreuve, str(request.POST.get("numero")))
    corrige = os.path.join(numero, "corrige")
    # matr = f.encrypt(str(i.matricule.matricule).encode())  # matr promotion cours session numero annee
    if os.path.isdir(annee):
        if os.path.isdir(promotion):
            if os.path.isdir(cours):
                if os.path.isdir(epreuve):
                    if os.path.isdir(numero):
                        if os.path.isdir(corrige):
                            for each_path in os.listdir(corrige):
                                if ".jpg" in each_path:
                                    ############################################################recuperer qrcode

                                    image = cv2.imread(os.path.join(corrige, each_path))
                                    qrCodeDetector = cv2.QRCodeDetector()
                                    decodedText, points, straight_qrcode = qrCodeDetector.detectAndDecode(image)
                                    if points is not None:
                                        #matr = fcryp.decrypt(str(decodedText).encode()).decode()
                                        matr = 1
                                        # ############################################################recuperer image note
                                        y=0
                                        x=80
                                        h=200
                                        w=1800
                                        crop = image[y:y+h, x:x+w]
                                        # ############################################################recuperer image note
                                        # ############################################################rotation/coller image note
                                        rotated_img = rotate_image(crop,51.32)
                                        l_img = cv2.imread(os.path.join(staticlink, "Ft.png"))
                                        x_offset=800
                                        y_offset=1300
                                        l_img[y_offset:y_offset+rotated_img.shape[0], x_offset:x_offset+rotated_img.shape[1]] = rotated_img
                                        resized = cv2.resize(l_img, (500,700), interpolation = cv2.INTER_AREA)
                                        pt=getpoint(resized)
                                        if pt==-1:# les bulles ne sont pas 13
                                            tempjournalcote.objects.create(
                                                matricule_id=matr,
                                                lien=str(lientxt),
                                                user=request.user,
                                                obs="les bulles ne sont pas 13"
                                            )
                                        elif pt==-2:# aucun bulle cocher
                                            tempjournalcote.objects.create(
                                                matricule_id=matr,
                                                lien=str(lientxt),
                                                user=request.user,
                                                obs="aucun bulle cocher"
                                            )

                                        elif pt==-3:# plusieurs bulle cocher
                                            tempjournalcote.objects.create(
                                                matricule_id=matr,
                                                lien=str(lientxt),
                                                user=request.user,
                                                obs="plusieurs bulle cocher"
                                            )
                                        else:
                                            c=cote.objects.filter(
                                                    matricule_id=matr,
                                                    cours_id=request.POST.get("cours"),
                                                    sesionn=request.POST.get("epreuve"),
                                                    numero=request.POST.get("numero"),
                                                    promotion_id=request.POST.get("promotion"),
                                                    annee_id=request.POST.get("annee"))
                                            if c:
                                                if request.user.has_perm("cote.change_cote"):
                                                    c.update(
                                                        user=request.user,
                                                        lien=str(lientxt),
                                                        cote=float(pt))
                                                    calculerpourcentage(request.POST.get("annee"),
                                                                        request.POST.get("promotion"),
                                                                        request.POST.get("cours"),
                                                                        request.POST.get("epreuve"),matr)
                                                else:
                                                    tempjournalcote.objects.create(
                                                        matricule_id=matr,
                                                        lien=str(lientxt),
                                                        user=request.user,
                                                        obs="Utilisateur n'a pas le droit de modifier"
                                                    )
                                            else:

                                                if request.user.has_perm("cote.add_cote"):
                                                    cote.objects.create(
                                                        matricule_id=matr,
                                                        cours_id=request.POST.get("cours"),
                                                        sesionn=request.POST.get("epreuve"),
                                                        numero=request.POST.get("numero"),
                                                        user=request.user,
                                                        lien=str(lientxt),
                                                        cote=float(pt),
                                                        promotion_id=request.POST.get("promotion"),
                                                        annee_id=request.POST.get("annee"))
                                                    calculerpourcentage(request.POST.get("annee"),
                                                                        request.POST.get("promotion"),
                                                                        request.POST.get("cours"),
                                                                        request.POST.get("epreuve"), matr)
                                                else:
                                                    tempjournalcote.objects.create(
                                                        matricule_id=matr,
                                                        lien=str(lientxt),
                                                        user=request.user,
                                                        obs="Utilisateur n'a pas le droit d'aujout"
                                                    )
                                        ############################################################coller image note
                                    else:
                                        pass
                                        #print("QR code not detected")
                                    ############################################################recuperer qrcode

                        return HttpResponse()
    return HttpResponseForbidden()




@login_required
@require_POST
def deletefile(request):
    # if request.user.is_superuser:
    #     pass
    # # elif request.user.has_perm("archiv.electronique"):
    # #     pass
    # # elif request.user.has_perm("archiv.direction"):
    # #     pass
    # elif request.user.has_perm("archiv.physique"):
    #     return HttpResponse("")
    if os.path.exists(settings.MEDIA_ROOT + '/'+request.POST.get("id")):
        os.remove(settings.MEDIA_ROOT + '/'+request.POST.get("id"))
    return HttpResponse("")

