from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from .models import User
from django.contrib.auth import login,logout, authenticate 
from django.contrib.auth.decorators import login_required
import logging
import os
import glob
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from collegeEntrepreneur.models import Entreprise,specialites,Distinctions,Activite,Partenaire,ProduitService,Certification
from collegeEntrepreneur.models import Notification,Annexe
from django.core.serializers import serialize
# from products.serializers import ENTREPRISESerializer,DistinctionSerializer

#Variable that can be everytime overrite to register the connected users actions
user_actions_logger = logging.getLogger('user_actions')

import datetime

#home page for admin
@login_required
def index_admin(request):
    
    meilleur_femme=None
    meilleur_homme=None
    
    user=request.user
    
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
            
    notifications=Notification.objects.filter(recipient=request.user)
    nombre_total_notification=len(notifications)
    nombre_total_entreprise=len(Entreprise.objects.all())
    specialites_disponibles = ["SPECIALITE"+str(i) for i in range(1,68,1)]
    
    

    top_entreprises=Entreprise.objects.all().order_by('-budget_rang')[:3]
    
    if len(top_entreprises)!=0:
        if top_entreprises[0].responsable.sexe=="F":
            meilleur_femme=top_entreprises[0]
        elif top_entreprises[0].responsable=='M':
            meilleur_homme=top_entreprises[0]
            
    if meilleur_femme==None:
        for i in Entreprise.objects.all().order_by('-budget_rang'):
            if i.responsable.sexe=="F":
                meilleur_femme=i
                break
            
    if meilleur_homme==None:
        for i in Entreprise.objects.all().order_by('-budget_rang'):
            if i.responsable.sexe=="M":
                meilleur_homme=i
                break
            
            
            
    
    # Get today date 
    date_actuelle = datetime.date.today()

    # Extract the year part of the date
    annee_actuel = date_actuelle.year
    
    nombre_total_entrepreneurs=len(User.objects.filter(user_category="utilisateur"))
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a consulté la page d'accueil des admins.")
    context={
        "nombre_total_entreprise":nombre_total_entreprise,
        "nombre_total_entrepreneurs":nombre_total_entrepreneurs,
        "top_entreprises":top_entreprises,
        "user":user,
        "notifications":notifications,
        "nombre_total_notification":nombre_total_notification,
        "nombre_distinction":len(Distinctions.objects.all()),
        "meilleur_homme":Distinctions.objects.filter(annee=annee_actuel,status="Entrepreneur de la annee").first(),
        "meilleur_femme":Distinctions.objects.filter(annee=annee_actuel,status="Entrepreneur femme de la annee").first(),
        "meilleur_honore":Distinctions.objects.filter(annee=annee_actuel,status="Entrepreneur de le honore").first()
        
        }
    
    for index,i in enumerate(specialites_disponibles):
        context[f'specialite{index+1}']=Entreprise.objects.filter(specialite=i).order_by('-budget_rang')[:3]
        context[f'specialitejson{index+1}']=json.dumps([ENTREPRISESerializer(item).data for item in Entreprise.objects.filter(specialite=i).order_by('-budget_rang')[:3]])
        
    
    return render(request,"account/admin/index.html",context)
    
    




#Home page of users(entrepreneurs)
@login_required
def index_utilisateur(request):
    
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
            
    print(request.user.entreprise)  
    nombre_total_entreprise=len(Entreprise.objects.all())
    specialites_disponibles = ["SPECIALITE"+str(i) for i in range(1,68,1)]
    top_entreprises=Entreprise.objects.all().order_by('-budget_rang')[:3]
    
    nombre_distinction=len(top_entreprises)*2
    entreprise_u = Entreprise.objects.filter(responsable=request.user.id).order_by('id').first()
    nombre_total_entrepreneurs=len(User.objects.filter(user_category="utilisateur"))
    startups=Entreprise.objects.filter(responsable=request.user)
    def check_startup_user(item):
        if len(item)>=1:
            return item[0]
        else:
            return None
            
    one_company_user=check_startup_user(startups)
    
    def user_one_company_activites_and_service(item):
        
        if item is not None:
            if item.activites is not None:
                nombre_activites=item.activites.count()
            else:
                nombre_activites=0
            if item.produit_services is not None:
                nombre_produit_services=item.produit_services.count()
            else:
                nombre_produit_services=0
                
            return nombre_activites,nombre_produit_services
        
    activites_user_company,produits_service_user_company=user_one_company_activites_and_service(one_company_user)
        
    actuel_user=request.user
    notifications=Notification.objects.filter(recipient=request.user)
    nombre_total_notification=len(notifications)
    context={
        "nombre_total_entreprise":nombre_total_entreprise,
        "nombre_total_entrepreneurs":nombre_total_entrepreneurs,
        "one_company_user":one_company_user,
        "top_entreprises":top_entreprises,
        "actuel_user":actuel_user,
        "activites_user_company":activites_user_company,
        "produits_service_user_company":produits_service_user_company,
        "user":request.user,
        "notifications":notifications,
        "nombre_total_notification":nombre_total_notification,
        "nombre_distinction":len(Distinctions.objects.all()),
        }
    
    for index,i in enumerate(specialites_disponibles):
        context[f'specialite{index+1}']=Entreprise.objects.filter(specialite=i).order_by('-budget_rang')[:3]
        
        context[f'specialitejson{index+1}']=json.dumps([ENTREPRISESerializer(item).data for item in Entreprise.objects.filter(specialite=i).order_by('-budget_rang')[:3]])
        if entreprise_u.specialite==i:
            context['specialite_u']=Entreprise.objects.filter(specialite=i).order_by('-budget_rang')[:3]
            
            rep=Entreprise.objects.filter(specialite=i).order_by('-budget_rang')
            
        
            
           

            index = None

            for j, entreprise in enumerate(rep):
                if entreprise == entreprise_u:
                   index = j+1
                   break
            print(index)
            if index>3:
                context['entreprise_user_now']=entreprise_u
            else:
                context['entreprise_user_now']=None
                
            context["index"]=index
            print(index)
    
            
    
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a consulté la page d'accueil des élèves.")
    return render(request,"account/utilisateur/index.html",context)

import json
#Entreprises page view of admin
@login_required
def entreprises_admin(request):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    entrepreneurs=User.objects.filter(user_category="utilisateur")
    nombre_cooperative=len(Entreprise.objects.filter(Q(type='cooperative') | Q(type="Cooperative")))
    nombre_entreprise=len(Entreprise.objects.all())
    nombre_ong=len(Entreprise.objects.filter(Q(type="ong") | Q(type="ONG")))
    nombre_societe=len(Entreprise.objects.filter(Q(type="societe") | Q(type='Societe')))
    entreprises=Entreprise.objects.all()
    specialites_disponibles = ["SPECIALITE"+str(i) for i in range(1,68,1)]
    
    serialized_enterprises = [ENTREPRISESerializer(entreprise).data for entreprise in entreprises]
    serialized_enterprises=serialized_enterprises = json.dumps(serialized_enterprises)
    
    if request.method=="POST":
        description=request.POST.get('description',"")
        nombre_employe=request.POST.get('nombre_employe',"")
        adresse_localisation=request.POST.get('adresse_localisation',"")
        domaine_activite=request.POST.get('domaine_activite',"")
        type=request.POST.get("type","")
        telephon=request.POST.get('telephon',"")
        mail=request.POST.get('mail',"")
        date_creation=request.POST.get('date_creation','')
        matricule=request.POST.get('matricule',"")
        num_ifu=request.POST.get('num_ifu','')
        rccm=request.POST.get('rccm','')
        nom=request.POST.get('nom','')
        whatsapp=request.POST.get('whatsapp',"")
        logo=request.FILES.get('logo',"")
        responsable=request.POST.get('responsable')
        responsable=User.objects.get(id=responsable)
        specialite=request.POST.get('specialite',"")
        
        if whatsapp=="":
            whatsapp=None
        if logo=="":
            logo=None
            
        entrep=Entreprise(
            description=description,
            nombre_employe=nombre_employe,
            adresse_localisation=adresse_localisation,
            domaine_activite=domaine_activite,
            type=type,
            telephon=telephon,
            mail=mail,
            date_creation=date_creation,
            matricule=matricule,
            num_ifu=num_ifu,
            rccm=rccm,
            nom=nom,
            whatsapp=whatsapp,
            logo=logo,
            responsable=responsable,
            specialite=specialite
        )
        
        entrep.save()
        
        if entrep is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a créé une entreprise de nom : {entrep.nom}.")
        
        return redirect("entreprises-admin")
    notifications=Notification.objects.filter(recipient=request.user)
    nombre_total_notification=len(notifications)
        
    context={
        "entrepreneurs":User.objects.filter(user_category="utilisateur"),
        "nombre_cooperative":nombre_cooperative,
        'nombre_entreprise':nombre_entreprise,
        'nombre_ong':nombre_ong,
        'nombre_societe':nombre_societe,
        'entreprises':entreprises,
        'entreprise_test':serialized_enterprises,
        "user":request.user,
        "notifications":notifications,
        "nombre_total_notification":nombre_total_notification
        }
    for index,i in enumerate(specialites_disponibles):
        context[f'specialite{index+1}']=Entreprise.objects.filter(specialite=i).order_by('-budget_rang')
        context[f'specialitejson{index+1}']=json.dumps([ENTREPRISESerializer(item).data for item in Entreprise.objects.filter(specialite=i).order_by('-budget_rang')])
        
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a consulté la page de la liste des entreprises.")
    return render(request,"account/admin/entreprises.html",context)



#Entreprise update view admin
@login_required
def entreprises_update_admin(request,id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    entrepreneurs=User.objects.filter(user_category="utilisateur")
    nombre_cooperative=len(Entreprise.objects.filter(Q(type='cooperative') | Q(type="Cooperative")))
    nombre_entreprise=len(Entreprise.objects.all())
    nombre_ong=len(Entreprise.objects.filter(Q(type="ong") | Q(type="ONG")))
    nombre_societe=len(Entreprise.objects.filter(Q(type="societe") | Q(type='Societe')))
    entreprises=Entreprise.objects.all()
    if request.method=="POST":
        description=request.POST.get('description',"")
        nombre_employe=request.POST.get('nombre_employe',"")
        adresse_localisation=request.POST.get('adresse_localisation',"")
        domaine_activite=request.POST.get('domaine_activite',"")
        type=request.POST.get("type","")
        telephon=request.POST.get('telephon',"")
        mail=request.POST.get('mail',"")
        date_creation=request.POST.get('date_creation','')
        matricule=request.POST.get('matricule',"")
        num_ifu=request.POST.get('num_ifu','')
        rccm=request.POST.get('rccm','')
        nom=request.POST.get('nom','')
        whatsapp=request.POST.get('whatsapp',"")
        logo=request.FILES.get('logo',"")
        responsable=request.POST.get('responsable')
        responsable=User.objects.get(id=responsable)
        specialite=request.POST.get('specialite',"")
        
        if whatsapp=="":
            whatsapp=None
        if logo=="":
            logo=None
        
        entrep=Entreprise(
            id=id,
            description=description,
            nombre_employe=nombre_employe,
            adresse_localisation=adresse_localisation,
            domaine_activite=domaine_activite,
            type=type,
            telephon=telephon,
            mail=mail,
            date_creation=date_creation,
            matricule=matricule,
            num_ifu=num_ifu,
            rccm=rccm,
            nom=nom,
            whatsapp=whatsapp,
            logo=logo,
            responsable=responsable,
            specialite=specialite
        )
        
        entrep.save()
        
        if entrep is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a modifié une entreprise de nom : {entrep.nom}.")
        
        return redirect("entreprises-admin")
        
    notifications=Notification.objects.filter(recipient=request.user)
    nombre_total_notification=len(notifications)
    context={
        "entrepreneurs":entrepreneurs,
        "nombre_cooperative":nombre_cooperative,
        'nombre_entreprise':nombre_entreprise,
        'nombre_ong':nombre_ong,
        'nombre_societe':nombre_societe,
        'entreprises':entreprises,
        "user":request.user,
        "notifications":notifications,
        "nombre_total_notification":nombre_total_notification
        }
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a consulté la page de la liste des entreprises.")
    return render(request,"account/admin/entreprises.html",context)


#Entreprise delete view admin
@login_required
def entreprises_delete_admin(request,id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    entreprise=Entreprise.objects.get(id=id)
    entreprise.delete()
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a supprimé une entreprise .")
    return redirect("entreprises-admin")


#Company detail view admin
@login_required
def company_detail_admin(request,id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    entreprise_user=Entreprise.objects.get(id=id)
    print(entreprise_user)
    activites=entreprise_user.activites.all()
    produits=entreprise_user.produit_services.all()
    partenaires=entreprise_user.partenaires.all()
    certifications=entreprise_user.certifications.all()
    annexes=entreprise_user.annexes.all()
    
    if request.method=="POST":
        description=request.POST.get('description',"")
        nombre_employe=request.POST.get('nombre_employe',"")
        adresse_localisation=request.POST.get('adresse_localisation',"")
        domaine_activite=request.POST.get('domaine_activite',"")
        type=request.POST.get("type","")
        telephon=request.POST.get('telephon',"")
        mail=request.POST.get('mail',"")
        date_creation=request.POST.get('date_creation','')
        matricule=request.POST.get('matricule',"")
        num_ifu=request.POST.get('num_ifu','')
        rccm=request.POST.get('rccm','')
        nom=request.POST.get('nom','')
        whatsapp=request.POST.get('whatsapp',"")
        logo=request.FILES.get('logo',"")
        specialite=request.POST.get('specialite',"")
        
        
        if not logo:
            logo=None
            
        entreprise=Entreprise(
                    id=entreprise_user.id,
                    description=description,
                    nombre_employe=nombre_employe,
                    adresse_localisation=adresse_localisation,
                    domaine_activite=domaine_activite,
                    type=type,
                    telephon=telephon,
                    mail=mail,
                    date_creation=date_creation,
                    matricule=matricule,
                    num_ifu=num_ifu,
                    rccm=rccm,
                    nom=nom,
                    whatsapp=whatsapp,
                    logo=logo,
                    specialite=specialite,
                    responsable=entreprise_user.responsable
                )
        entreprise.save()
        if entreprise is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a fait la mise à jour des infos de l'entreprise {entreprise_user.nom}")
            return redirect(reverse("company-detail-admin",args=[entreprise.id]))
    notifications=Notification.objects.filter(recipient=request.user)
    nombre_total_notification=len(notifications)
    context={"entreprise":entreprise_user,
             "user":request.user,
             "activites":activites,
             "produits":produits,
             "partenaires":partenaires,
             "certifications":certifications,
             "annexes":annexes,
             "user":request.user,
            "notifications":notifications,
            "nombre_total_notification":nombre_total_notification
             }

    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a consulté la page de la liste des entreprises.")
    return render(request,"account/admin/compagny-detail.html",context)




# create activite admin
@login_required
def company_create_activite_admin(request,company_id):  
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur() 
    entreprise=Entreprise.objects.get(id=company_id)

    
    if request.method=="POST":
        denomination=request.POST.get('denomination')
        description=request.POST.get("description")
        date_lancement=request.POST.get('date_lancement')
        chiffreaffaire=request.POST.get('chiffreaffaire')
        depenses=request.POST.get('depenses')
        
        activite=Activite(
                denomination=denomination,
                description=description,
                date_lancement=date_lancement,
                chiffreaffaire=chiffreaffaire,
                depenses=depenses,
                entreprise=entreprise
        )
        activite.save()
        if activite is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a ajouté une activité à son entreprise {entreprise.nom}.")
            
        return redirect(reverse("company-detail-admin",args=[entreprise.id]))
    return redirect(reverse("company-detail-admin",args=[entreprise.id]))


#Update activite admin view
@login_required
def company_update_activite_admin(request,company_id,id):
    
            
    entreprise=Entreprise.objects.get(id=company_id)

    
    if request.method=="POST":
        denomination=request.POST.get('denomination')
        description=request.POST.get("description")
        date_lancement=request.POST.get('date_lancement')
        chiffreaffaire=request.POST.get('chiffreaffaire')
        depenses=request.POST.get('depenses')
        
        activite=Activite(
                id=id,
                denomination=denomination,
                description=description,
                date_lancement=date_lancement,
                chiffreaffaire=chiffreaffaire,
                depenses=depenses,
                entreprise=entreprise
        )
        activite.save()
        if activite is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a modifé une activité de son entreprise {entreprise.nom}.")
            
        return redirect(reverse("company-detail-admin",args=[entreprise.id]))
    return redirect(reverse("company-detail-admin",args=[entreprise.id]))


#Delete activity admin
@login_required
def company_delete_activite_admin(request,company_id,id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    entreprise=Entreprise.objects.get(id=company_id)
    activite=Activite.objects.get(id=id)
    
    activite.delete()
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a supprimé une activité de son entreprise.")
    return redirect(reverse("company-detail-admin",args=[entreprise.id]))


#Create Produits Services admin
@login_required
def company_create_produits_admin(request,company_id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    
    
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    
    
    
    entreprise=Entreprise.objects.get(id=company_id)
    
    if request.method=="POST":
        nom_produit_service=request.POST.get('nom_produit_service')
        date_lancementproduitservice=request.POST.get('date_lancementproduitservice')
        descriptionproduitservice=request.POST.get('descriptionproduitservice')
        prix_tarifaire=request.POST.get('prix_tarifaire')
        chiffreAffaire=request.POST.get('chiffreAffaire')
        depenses=request.POST.get('depenses')
        
        
        
        produit=ProduitService(
            nom_produit_service=nom_produit_service,
            date_lancementproduitservice=date_lancementproduitservice,
            descriptionproduitservice=descriptionproduitservice,
            prix_tarifaire=prix_tarifaire,
            chiffreAffaire=chiffreAffaire,
            depenses=depenses,
            entreprise=entreprise
        )
        produit.save()
        if produit is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a ajouté un produit ou service à son entreprise {entreprise.nom}.")
        return redirect(reverse("company-detail-admin",args=[entreprise.id]))
    return redirect(reverse("company-detail-admin",args=[entreprise.id]))


#Update Produits Services admin
@login_required
def company_update_produits_admin(request,company_id,id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    
    
    
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    
    
    
    entreprise=Entreprise.objects.get(id=company_id)
    
    if request.method=="POST":
        nom_produit_service=request.POST.get('nom_produit_service')
        date_lancementproduitservice=request.POST.get('date_lancementproduitservice')
        descriptionproduitservice=request.POST.get('descriptionproduitservice')
        prix_tarifaire=request.POST.get('prix_tarifaire')
        chiffreAffaire=request.POST.get('chiffreAffaire')
        depenses=request.POST.get('depenses')
        
        
        
        produit=ProduitService(
            id=id,
            nom_produit_service=nom_produit_service,
            date_lancementproduitservice=date_lancementproduitservice,
            descriptionproduitservice=descriptionproduitservice,
            prix_tarifaire=prix_tarifaire,
            chiffreAffaire=chiffreAffaire,
            depenses=depenses,
            entreprise=entreprise
        )
        produit.save()
        if produit is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a modifié un produit ou service de son entreprise {entreprise.nom}.")
        return redirect(reverse("company-detail-admin",args=[entreprise.id]))
    return redirect(reverse("company-detail-admin",args=[entreprise.id]))


#Delete Produits Services admin
@login_required
def company_delete_produits_admin(request,company_id,id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    
    
    
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    
    
    entreprise=Entreprise.objects.get(id=company_id)
    produit=ProduitService.objects.filter(id=id)
    produit.delete()
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a supprimée un produit ou service de son entreprise")
    return redirect(reverse("company-detail-admin",args=[entreprise.id]))


#Create Partenaire  admin
@login_required
def company_create_partenaire_admin(request,company_id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    
    
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    
    
    
    
    entreprise=Entreprise.objects.get(id=company_id)
    
    
    if request.method=="POST":
        nom_partenaire=request.POST.get('nom_partenaire')
        rccm=request.POST.get('rccm')
        numero_ifu=request.POST.get('numero_ifu')
        matricule=request.POST.get('matricule')
        date_de_creation=request.POST.get('date_de_creation')
        email=request.POST.get('email')
        type_entreprise=request.POST.get('type_entreprise')
        telephone=request.POST.get('telephone')
        adresse_localisation=request.POST.get('adresse_localisation')
        responsable=request.POST.get('responsable')
        mail_responsable=request.POST.get('mail_responsable')
        telephone_responsable=request.POST.get('telephone_responsable')
        domaine_activite=request.POST.get('domaine_activite')
        
        partenaire=Partenaire(
            entreprise=entreprise,
            nom_partenaire=nom_partenaire,
            rccm=rccm,
            numero_ifu=numero_ifu,
            matricule=matricule,
            date_de_creation=date_de_creation,
            email=email,
            type_entreprise=type_entreprise,
            telephone_responsable=telephone_responsable,
            telephone=telephone,
            adresse_localisation=adresse_localisation,
            responsable=responsable,
            mail_responsable=mail_responsable,
            domaine_activite=domaine_activite
        )
        
        partenaire.save()
        
        if partenaire is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a ajouté un partenaire à son entreprise {entreprise.nom}.")
        return redirect(reverse("company-detail-admin",args=[entreprise.id]))
    return redirect(reverse("company-detail-admin",args=[entreprise.id]))


#Update Partenaire  admin
@login_required
def company_update_partenaire_admin(request,company_id,id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    
    
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    
    
    
    entreprise=Entreprise.objects.get(id=company_id)
    
    
    
    if request.method=="POST":
        nom_partenaire=request.POST.get('nom_partenaire')
        rccm=request.POST.get('rccm')
        numero_ifu=request.POST.get('numero_ifu')
        matricule=request.POST.get('matricule')
        date_de_creation=request.POST.get('date_de_creation')
        email=request.POST.get('email')
        type_entreprise=request.POST.get('type_entreprise')
        telephone=request.POST.get('telephone')
        adresse_localisation=request.POST.get('adresse_localisation')
        responsable=request.POST.get('responsable')
        mail_responsable=request.POST.get('mail_responsable')
        telephone_responsable=request.POST.get('telephone_responsable')
        domaine_activite=request.POST.get('domaine_activite')
        
        partenaire=Partenaire(
            id=id,
            entreprise=entreprise,
            nom_partenaire=nom_partenaire,
            rccm=rccm,
            numero_ifu=numero_ifu,
            matricule=matricule,
            date_de_creation=date_de_creation,
            email=email,
            type_entreprise=type_entreprise,
            telephone_responsable=telephone_responsable,
            telephone=telephone,
            adresse_localisation=adresse_localisation,
            responsable=responsable,
            mail_responsable=mail_responsable,
            domaine_activite=domaine_activite
        )
        
        partenaire.save()
        
        if partenaire is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a fait la mise à jour des informtions de l'un de ses partenaires .")
        return redirect(reverse("company-detail-admin",args=[entreprise.id]))
    return redirect(reverse("company-detail-admin",args=[entreprise.id]))


#Delete Partenaire  admin
@login_required
def company_delete_partenaire_admin(request,company_id,id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    
    
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    
    
    entreprise=Entreprise.objects.get(id=company_id)
    partenaire=Partenaire.objects.filter(id=id)
    partenaire.delete()
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a supprimée un partenaire de son entreprise")
    return redirect(reverse("company-detail-admin",args=[entreprise.id]))



#Create certification  admin
@login_required
def company_create_certification_admin(request,company_id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    
    
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    
    
    
    entreprise=Entreprise.objects.get(id=company_id)
    
    if request.method=="POST":
        nom=request.POST.get('nom')
        numero_certification=request.POST.get('numero_certification')
        type=request.POST.get('type')
        date_delivrance=request.POST.get('date_delivrance')
        organisme=request.POST.get('organisme')
        
        certification=Certification(
            entreprise=entreprise,
            nom=nom,
            numero_certification=numero_certification,
            type=type,
            date_delivrance=date_delivrance,
            organisme=organisme
        )
        certification.save()
        if certification is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a ajouté une certification à son entreprise {entreprise.nom}.")
        return redirect(reverse("company-detail-admin",args=[entreprise.id]))
    return redirect(reverse("company-detail-admin",args=[entreprise.id]))



#Update certification  admin
@login_required
def company_update_certification_admin(request,company_id,id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    
    
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    
    
    
    entreprise=Entreprise.objects.get(id=company_id)
    
    if request.method=="POST":
        nom=request.POST.get('nom')
        numero_certification=request.POST.get('numero_certification')
        type=request.POST.get('type')
        date_delivrance=request.POST.get('date_delivrance')
        organisme=request.POST.get('organisme')
        
        certification=Certification(
            id=id,
            entreprise=entreprise,
            nom=nom,
            numero_certification=numero_certification,
            type=type,
            date_delivrance=date_delivrance,
            organisme=organisme
        )
        certification.save()
        if certification is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a ajouté une certification à son entreprise {entreprise.nom}.")
        return redirect(reverse("company-detail-admin",args=[entreprise.id]))
    return redirect(reverse("company-detail-admin",args=[entreprise.id]))



#Delete certification  admin
@login_required
def company_delete_certification_admin(request,company_id,id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    
    
    
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    
    
    entreprise=Entreprise.objects.get(id=company_id)
    certification=Certification.objects.filter(id=id)
    certification.delete()
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a supprimée une certification de son entreprise")
    return redirect(reverse("company-detail-admin",args=[entreprise.id]))



#Create annexe  admin
@login_required
def company_create_annexe_admin(request,company_id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    
    
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    
    
    entreprise=Entreprise.objects.get(id=company_id)
    
    if request.method=="POST":
        denomination=request.POST.get('denomination',"")
        responsable=request.POST.get('responsable',"")
        date_creation=request.POST.get('date_creation','')
        localisation=request.POST.get('localisation','')
        domaine_activite=request.POST.get('domaine_activite',"")
        tel_responsable=request.POST.get('tel_responsable',"")
        mail_responsable=request.POST.get('mail_responsable',"")
        
        annexe=Annexe(
            denomination=denomination,
            responsable=responsable,
            date_creation=date_creation,
            localisation=localisation,
            domaine_activite=domaine_activite,
            tel_responsable=tel_responsable,
            mail_responsable=mail_responsable,
            entreprise=entreprise
        )
        
        annexe.save()
        
        if annexe is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a ajouté une annexe à son entreprise {entreprise.nom}")
        return redirect(reverse("company-detail-admin",args=[entreprise.id]))
    return redirect(reverse("company-detail-admin",args=[entreprise.id]))



#Delete annexe  admin
@login_required
def company_delete_annexe_admin(request,company_id,id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    
    entreprise=Entreprise.objects.get(id=company_id)
    annexe=Annexe.objects.filter(id=id)
    annexe.delete()
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a supprimée une annexe de l'entreprise {entreprise.nom}")
    return redirect(reverse("company-detail-admin",args=[entreprise.id]))





#Update annexe  admin
@login_required
def company_update_annexe_admin(request,company_id,id):
    entreprise=Entreprise.objects.get(id=company_id)
    
    if request.method=="POST":
        denomination=request.POST.get('denomination',"")
        responsable=request.POST.get('responsable',"")
        date_creation=request.POST.get('date_creation','')
        localisation=request.POST.get('localisation','')
        domaine_activite=request.POST.get('domaine_activite',"")
        tel_responsable=request.POST.get('tel_responsable',"")
        mail_responsable=request.POST.get('mail_responsable',"")
        
        annexe=Annexe(
            id=id,
            denomination=denomination,
            responsable=responsable,
            date_creation=date_creation,
            localisation=localisation,
            domaine_activite=domaine_activite,
            tel_responsable=tel_responsable,
            mail_responsable=mail_responsable,
            entreprise=entreprise
        )
        
        annexe.save()
        
        if annexe is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a modifié une annexe de l' entreprise {entreprise.nom}")
        return redirect(reverse("company-detail-admin",args=[entreprise.id]))
    return redirect(reverse("company-detail-admin",args=[entreprise.id]))

#end














#Distinction view admin
@login_required
def distinctions_admin(request):

    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    
    notifications=Notification.objects.filter(recipient=request.user) 
    nombre_total_notification=len(notifications)
    top_entreprises=Entreprise.objects.all().order_by('-budget_rang')[:3]
    
    nombre_distinction=len(top_entreprises)*2
    
    entrepreneurs_nommine=len(top_entreprises)
    specialites_disponibles = ["SPECIALITE"+str(i) for i in range(1,68,1)]
    nombre_homme=[i for i in top_entreprises if i.responsable.sexe=="M"]
    
    nombre_homme=len(nombre_homme)
    nombre_femme=[i for i in top_entreprises if i.responsable.sexe=="F"]
    nombre_femme=len(nombre_femme)
    
    distinctions=Distinctions.objects.all().order_by("-annee")
    
    for item in distinctions:
        print(item.entreprise)
    
    if request.method=="POST":
        user=request.POST.get('user',"")
        entreprise = Entreprise.objects.filter(responsable=user).order_by('id').first()
        user=User.objects.get(id=user)
        annee=request.POST.get('annee',"")
        status=request.POST.get('status',"")
        
        distinction=Distinctions(
            entreprise=entreprise,
            annee=annee,
            status=status,
            user=user
        )
        distinction.save()
        if distinction is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a ajouté une distinction.")
            return redirect("distinctions-admin")
        
    if Distinctions.objects.first():
        femme_distinction=Distinctions.objects.first().nombre_femme
    else:
        femme_distinction=0
    
    if Distinctions.objects.first():
        homme_distinction=Distinctions.objects.first().nombre_homme  
    else:
        homme_distinction=0

    
    context={
        "user":request.user,
        "entrepreneurs":User.objects.filter(user_category="utilisateur"),
        "notifications":notifications,
        "nombre_total_notification":nombre_total_notification,
        "nombre_distinction":nombre_distinction,
        "top_entreprises":top_entreprises,
        "nombre_femme":femme_distinction,
        "nombre_homme":homme_distinction,
        "entrepreneurs_nommine":len(Distinctions.objects.all()),
        "nombre_honore":len(Distinctions.objects.filter(status="Entrepreneur de le honore")),
        "distinctions":distinctions,
        "distinctionjson":json.dumps([DistinctionSerializer(item).data for item in Distinctions.objects.all()])
        
    }
    for index,i in enumerate(specialites_disponibles):
        context[f'specialite{index+1}']=Entreprise.objects.filter(specialite=i).order_by('-budget_rang')
        context[f'specialitejson{index+1}']=json.dumps([ENTREPRISESerializer(item).data for item in Entreprise.objects.filter(specialite=i).order_by('-budget_rang')])
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a consulté la page de la liste des distinctions.")
    return render(request,"account/admin/distinctions.html",context)



#entrepreneurs admin view(read, create,)
@login_required
def entrepreneurs_admin(request):
    entrepreneurs=User.objects.filter(user_category="utilisateur")
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    entreprises=Entreprise.objects.all()
    entrepreneurs_femme=len(User.objects.filter(Q(user_category="utilisateur") & Q(sexe="F")))
    entrepreneurs_homme=len(User.objects.filter(Q(user_category="utilisateur") & Q(sexe="M")))
    nombre_entrepreneurs=len(entrepreneurs)
    specialites_disponibles = ["SPECIALITE"+str(i) for i in range(1,68,1)]
    if request.method == 'POST':
        #user info
        photo=request.FILES.get('photo',"")
        promotion=request.POST.get('promotion',"")
        lieu_de_residence=request.POST.get('lieu_de_residence',"")
        date_inscription=request.POST.get("date_inscription","")
        telephone=request.POST.get('telephone',"")
        date_naissance=request.POST.get('date_naissance',"")
        sexe=request.POST.get('sexe',"")
        last_name=request.POST.get('last_name')
        first_name=request.POST.get('first_name')
        password=request.POST.get("password")
        email=request.POST.get('email')
        
        if not promotion:
            promotion=None
            
        if not lieu_de_residence:
            lieu_de_residence=None
            
        if not date_naissance:
            date_naissance=None
        if not date_inscription:
            date_inscription=timezone.now()
            
        if not photo:
            photo=None
            
        if not telephone:
            telephone=None
        if not sexe:
            sexe=None
            
        
        user_category="utilisateur"
        
        #company info
        description=request.POST.get('description',"")
        nombre_employe=request.POST.get('nombre_employe',"")
        adresse_localisation=request.POST.get('adresse_localisation',"")
        domaine_activite=request.POST.get('domaine_activite',"")
        type=request.POST.get("type","")
        telephon=request.POST.get('telephon',"")
        mail=request.POST.get('mail',"")
        date_creation=request.POST.get('date_creation','')
        matricule=request.POST.get('matricule',"")
        num_ifu=request.POST.get('num_ifu','')
        rccm=request.POST.get('rccm','')
        nom=request.POST.get('nom','')
        whatsapp=request.POST.get('whatsapp',"")
        logo=request.FILES.get('logo',"")
        specialite=request.POST.get('specialite',"")
        
        
        if not logo:
            logo=None
        #create user here
        
        user=User.objects.create_user(
            first_name = first_name,
            last_name = last_name,
            email=email,
            sexe=sexe,
            user_category=user_category,
            lieu_de_residence=lieu_de_residence,
            date_naissance=date_naissance,
            date_inscription=date_inscription,
            telephone=telephone,
            promotion=promotion,
            photo=photo,
            password=password
            )
        
        if user is not None:
                entreprise=Entreprise(
                    description=description,
                    nombre_employe=nombre_employe,
                    adresse_localisation=adresse_localisation,
                    domaine_activite=domaine_activite,
                    type=type,
                    telephon=telephon,
                    mail=mail,
                    date_creation=date_creation,
                    matricule=matricule,
                    num_ifu=num_ifu,
                    rccm=rccm,
                    nom=nom,
                    whatsapp=whatsapp,
                    logo=logo,
                    specialite=specialite,
                    responsable=user
                )
                entreprise.save()
                if entreprise is not None:
                    user_actions_logger.info(f"Utilisateur {user.first_name} {user.last_name} est inscrit par {request.user.first_name} {request.user.last_name}.")
                    
                return redirect('entrepreneurs-admin') 
    notifications=Notification.objects.filter(recipient=request.user)
    nombre_total_notification=len(notifications)
    context={"entrepreneurs":entrepreneurs,
             "nombre_entrepreneurs":nombre_entrepreneurs,
             "entrepreneurs_homme":entrepreneurs_homme,
             "entrepreneurs_femme":entrepreneurs_femme,
             "entreprises":entreprises,
             "user":request.user,
            "notifications":notifications,
            "nombre_total_notification":nombre_total_notification
             }
    for index,i in enumerate(specialites_disponibles):
        context[f'specialite{index+1}']=Entreprise.objects.filter(specialite=i).order_by('-budget_rang')
        context[f'specialitejson{index+1}']=json.dumps([ENTREPRISESerializer(item).data for item in Entreprise.objects.filter(specialite=i).order_by('-budget_rang')])
     
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a consulté la page de la liste des entreprises.")
    return render(request,"account/admin/entrepreneurs.html",context)


from django.core.files import File #used to update file field


#Update entrepreneur  admin view
@login_required
def entrepreneurs_update_admin(request,id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    entrepreneurs=User.objects.filter(user_category="utilisateur")
    entrepreneurs_femme=len(User.objects.filter(Q(user_category="utilisateur") & Q(sexe="F")))
    entrepreneurs_homme=len(User.objects.filter(Q(user_category="utilisateur") & Q(sexe="M")))
    nombre_entrepreneurs=len(entrepreneurs)
    entreprises=Entreprise.objects.all()
    
    if request.method == 'POST':
        #user info
        photo=request.FILES.get('photo',"")
        promotion=request.POST.get('promotion',"")
        lieu_de_residence=request.POST.get('lieu_de_residence',"")
        date_inscription=request.POST.get("date_inscription","")
        telephone=request.POST.get('telephone',"")
        date_naissance=request.POST.get('date_naissance',"")
        sexe=request.POST.get('sexe',"")
        last_name=request.POST.get('last_name')
        first_name=request.POST.get('first_name')
        # password=request.POST.get("password")
        email=request.POST.get('email')
        
        if not promotion:
            promotion=None
            
        if not lieu_de_residence:
            lieu_de_residence=None
            
        if not date_naissance:
            date_naissance=None
        if not date_inscription:
            date_inscription=timezone.now()
            
        if not photo:
            photo=None
            
        if not telephone:
            telephone=None
        if not sexe:
            sexe=None
            
        
        user_category="utilisateur"
        
        #company info
        description=request.POST.get('description',"")
        nombre_employe=request.POST.get('nombre_employe',"")
        adresse_localisation=request.POST.get('adresse_localisation',"")
        domaine_activite=request.POST.get('domaine_activite',"")
        type=request.POST.get("type","")
        telephon=request.POST.get('telephon',"")
        mail=request.POST.get('mail',"")
        date_creation=request.POST.get('date_creation','')
        matricule=request.POST.get('matricule',"")
        num_ifu=request.POST.get('num_ifu','')
        rccm=request.POST.get('rccm','')
        nom=request.POST.get('nom','')
        whatsapp=request.POST.get('whatsapp',"")
        logo=request.FILES.get('logo',"")
        specialite=request.POST.get('specialite',"")
        
        
        if not logo:
            logo=None
        #create user here
        entreprise_here=Entreprise.objects.get(id=id)
        user=User.objects.get(id=entreprise_here.responsable.id)
        
        user.first_name = first_name
        user.last_name = last_name
        user.email=email
        user.sexe=sexe
        user.user_category=user_category
        user.lieu_de_residence=lieu_de_residence
        user.date_naissance=date_naissance
        user.date_inscription=date_inscription
        user.telephone=telephone
        user.promotion=promotion
        user.photo=File(photo)
        # user.password=password
        user.save()
        
        if user is not None:
                entreprise=Entreprise(
                    id=id,
                    description=description,
                    nombre_employe=nombre_employe,
                    adresse_localisation=adresse_localisation,
                    domaine_activite=domaine_activite,
                    type=type,
                    telephon=telephon,
                    mail=mail,
                    date_creation=date_creation,
                    matricule=matricule,
                    num_ifu=num_ifu,
                    rccm=rccm,
                    nom=nom,
                    whatsapp=whatsapp,
                    logo=logo,
                    responsable=user,
                    specialite=specialite
                )
                entreprise.save()
                if entreprise is not None:
                    user_actions_logger.info(f"Utilisateur {user.first_name} {user.last_name} est inscrit par {request.user.first_name} {request.user.last_name}.")
                    
                return redirect('entrepreneurs-admin')
    notifications=Notification.objects.filter(recipient=request.user) 
    nombre_total_notification=len(notifications)
    context={"entrepreneurs":User.objects.filter(user_category="utilisateur"),
             "nombre_entrepreneurs":nombre_entrepreneurs,
             "entrepreneurs_homme":entrepreneurs_homme,
             "entrepreneurs_femme":entrepreneurs_femme,
             "entreprises":entreprises,
             "user":request.user,
            "notifications":notifications,
            "nombre_total_notification":nombre_total_notification
             }
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a consulté la page de la liste des entreprises.")
    return render(request,"account/admin/entrepreneurs.html",context)



#Delete entrepreneur  admin view
@login_required
def entrepreneurs_delete_admin(request,id):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    
    
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    
    
    entrepreneur=User.objects.get(id=id)
    
    entrepreneur.delete()
    
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a supprimé un entrepreneur avec ses entreprises incluses")
    
    return redirect('entrepreneurs-admin')





#User detail admin view
@login_required
def user_detail_admin(request):

    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a consulté la page de la liste des entreprises.")
    notifications=Notification.objects.filter(recipient=request.user) 
    nombre_total_notification=len(notifications)
    context={
         "user":request.user,
            "notifications":notifications,
            "nombre_total_notification":nombre_total_notification
    }
    return render(request,"account/admin/user-detail.html")



#CRUD operations on entreprises properties users views
#start
@login_required
def entreprises_utilisateur(request):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    
    
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    
    startups=Entreprise.objects.filter(responsable=request.user)
    def check_startup_user(item):
        if len(item)>=1:
            return item[0]
        else:
            return None
            
    entreprise_user=check_startup_user(startups)
    activites=entreprise_user.activites.all()
    produits=entreprise_user.produit_services.all()
    partenaires=entreprise_user.partenaires.all()
    certifications=entreprise_user.certifications.all()
    annexes=entreprise_user.annexes.all()
    
    if request.method=="POST":
        description=request.POST.get('description',"")
        nombre_employe=request.POST.get('nombre_employe',"")
        adresse_localisation=request.POST.get('adresse_localisation',"")
        domaine_activite=request.POST.get('domaine_activite',"")
        type=request.POST.get("type","")
        telephon=request.POST.get('telephon',"")
        mail=request.POST.get('mail',"")
        date_creation=request.POST.get('date_creation','')
        matricule=request.POST.get('matricule',"")
        num_ifu=request.POST.get('num_ifu','')
        rccm=request.POST.get('rccm','')
        nom=request.POST.get('nom','')
        whatsapp=request.POST.get('whatsapp',"")
        logo=request.FILES.get('logo',"")
        specialite=request.POST.get('specialite',"")
        
        
        if not logo:
            logo=None
            
        entreprise=Entreprise(
                    id=entreprise_user.id,
                    description=description,
                    nombre_employe=nombre_employe,
                    adresse_localisation=adresse_localisation,
                    domaine_activite=domaine_activite,
                    type=type,
                    telephon=telephon,
                    mail=mail,
                    date_creation=date_creation,
                    matricule=matricule,
                    num_ifu=num_ifu,
                    rccm=rccm,
                    nom=nom,
                    whatsapp=whatsapp,
                    logo=logo,
                    responsable=request.user,
                    specialite=specialite
                )
        entreprise.save()
        if entreprise is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a fait la mise à jour des infos de son entreprises {entreprise_user.nom}")
    notifications=Notification.objects.filter(recipient=request.user) 
    nombre_total_notification=len(notifications)
    context={"entreprise":entreprise_user,"user":request.user,"activites":activites,"produits":produits,"partenaires":partenaires,"certifications":certifications,
             "user":request.user,
            "notifications":notifications,
            "nombre_total_notification":nombre_total_notification,
            "annexes":annexes,
            }

    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a consulté la page de la liste des entreprises.")
    return render(request,"account/utilisateur/entreprises.html",context)


#activite
@login_required
def entreprises_create_activite_utilisateur(request):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    
    
    
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    distinction_repartition()
    
    
    
    startups=Entreprise.objects.filter(responsable=request.user)
    def check_startup_user(item):
        if len(item)>=1:
            return item[0]
        else:
            return None
            
    entreprise=check_startup_user(startups)
    activites=entreprise.activites.all()

    
    if request.method=="POST":
        denomination=request.POST.get('denomination')
        description=request.POST.get("description")
        date_lancement=request.POST.get('date_lancement')
        chiffreaffaire=request.POST.get('chiffreaffaire')
        depenses=request.POST.get('depenses')
        
        activite=Activite(
                denomination=denomination,
                description=description,
                date_lancement=date_lancement,
                chiffreaffaire=chiffreaffaire,
                depenses=depenses,
                entreprise=entreprise
        )
        activite.save()
        if activite is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a ajouté une activité à son entreprise {entreprise.nom}.")
            
        return redirect('entreprises-utilisateur')
    return redirect('entreprises-utilisateur')

@login_required
def entreprises_update_activite_utilisateur(request,id):
    startups=Entreprise.objects.filter(responsable=request.user)
    def check_startup_user(item):
        if len(item)>=1:
            return item[0]
        else:
            return None
            
    entreprise=check_startup_user(startups)

    
    if request.method=="POST":
        denomination=request.POST.get('denomination')
        description=request.POST.get("description")
        date_lancement=request.POST.get('date_lancement')
        chiffreaffaire=request.POST.get('chiffreaffaire')
        depenses=request.POST.get('depenses')
        
        activite=Activite(
                id=id,
                denomination=denomination,
                description=description,
                date_lancement=date_lancement,
                chiffreaffaire=chiffreaffaire,
                depenses=depenses,
                entreprise=entreprise
        )
        activite.save()
        if activite is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a modifé une activité de son entreprise {entreprise.nom}.")
            
        return redirect('entreprises-utilisateur')
    return redirect('entreprises-utilisateur')

@login_required
def entreprises_delete_activite_utilisateur(request,id):
    
    activite=Activite.objects.filter(id=id)

    activite.delete()
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a supprimé une activité de son entreprise.")
    return redirect('entreprises-utilisateur')


#Produits Services
@login_required
def entreprises_create_produits_utilisateur(request):
    startups=Entreprise.objects.filter(responsable=request.user)
    def check_startup_user(item):
        if len(item)>=1:
            return item[0]
        else:
            return None
            
    entreprise=check_startup_user(startups)
    activites=entreprise.activites.all()
    
    if request.method=="POST":
        nom_produit_service=request.POST.get('nom_produit_service')
        date_lancementproduitservice=request.POST.get('date_lancementproduitservice')
        descriptionproduitservice=request.POST.get('descriptionproduitservice')
        prix_tarifaire=request.POST.get('prix_tarifaire')
        chiffreAffaire=request.POST.get('chiffreAffaire')
        depenses=request.POST.get('depenses')
        
        
        
        produit=ProduitService(
            nom_produit_service=nom_produit_service,
            date_lancementproduitservice=date_lancementproduitservice,
            descriptionproduitservice=descriptionproduitservice,
            prix_tarifaire=prix_tarifaire,
            chiffreAffaire=chiffreAffaire,
            depenses=depenses,
            entreprise=entreprise
        )
        produit.save()
        if produit is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a ajouté un produit ou service à son entreprise {entreprise.nom}.")
        return redirect('entreprises-utilisateur')
    return redirect('entreprises-utilisateur')

@login_required
def entreprises_update_produits_utilisateur(request,id):
    startups=Entreprise.objects.filter(responsable=request.user)
    def check_startup_user(item):
        if len(item)>=1:
            return item[0]
        else:
            return None
            
    entreprise=check_startup_user(startups)

    
    if request.method=="POST":
        nom_produit_service=request.POST.get('nom_produit_service')
        date_lancementproduitservice=request.POST.get('date_lancementproduitservice')
        descriptionproduitservice=request.POST.get('descriptionproduitservice')
        prix_tarifaire=request.POST.get('prix_tarifaire')
        chiffreAffaire=request.POST.get('chiffreAffaire')
        depenses=request.POST.get('depenses')
        
        
        
        produit=ProduitService(
            id=id,
            nom_produit_service=nom_produit_service,
            date_lancementproduitservice=date_lancementproduitservice,
            descriptionproduitservice=descriptionproduitservice,
            prix_tarifaire=prix_tarifaire,
            chiffreAffaire=chiffreAffaire,
            depenses=depenses,
            entreprise=entreprise
        )
        produit.save()
        if produit is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a modifié un produit ou service de son entreprise {entreprise.nom}.")
        return redirect('entreprises-utilisateur')
    return redirect('entreprises-utilisateur')

@login_required
def entreprises_delete_produits_utilisateur(request,id):
    produit=ProduitService.objects.filter(id=id)
    produit.delete()
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a supprimée un produit ou service de son entreprise")
    return redirect('entreprises-utilisateur')


#Partenaire
@login_required
def entreprises_create_partenaire_utilisateur(request):
    startups=Entreprise.objects.filter(responsable=request.user)
    def check_startup_user(item):
        if len(item)>=1:
            return item[0]
        else:
            return None
            
    entreprise=check_startup_user(startups)
    
    
    if request.method=="POST":
        nom_partenaire=request.POST.get('nom_partenaire')
        rccm=request.POST.get('rccm')
        numero_ifu=request.POST.get('numero_ifu')
        matricule=request.POST.get('matricule')
        date_de_creation=request.POST.get('date_de_creation')
        email=request.POST.get('email')
        type_entreprise=request.POST.get('type_entreprise')
        telephone=request.POST.get('telephone')
        adresse_localisation=request.POST.get('adresse_localisation')
        responsable=request.POST.get('responsable')
        mail_responsable=request.POST.get('mail_responsable')
        telephone_responsable=request.POST.get('telephone_responsable')
        domaine_activite=request.POST.get('domaine_activite')
        
        partenaire=Partenaire(
            entreprise=entreprise,
            nom_partenaire=nom_partenaire,
            rccm=rccm,
            numero_ifu=numero_ifu,
            matricule=matricule,
            date_de_creation=date_de_creation,
            email=email,
            type_entreprise=type_entreprise,
            telephone_responsable=telephone_responsable,
            telephone=telephone,
            adresse_localisation=adresse_localisation,
            responsable=responsable,
            mail_responsable=mail_responsable,
            domaine_activite=domaine_activite
        )
        
        partenaire.save()
        
        if partenaire is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a ajouté un partenaire à son entreprise {entreprise.nom}.")
        return redirect('entreprises-utilisateur')
    return redirect('entreprises-utilisateur')


@login_required
def entreprises_update_partenaire_utilisateur(request,id):
    startups=Entreprise.objects.filter(responsable=request.user)
    def check_startup_user(item):
        if len(item)>=1:
            return item[0]
        else:
            return None
            
    entreprise=check_startup_user(startups)
    
    
    
    if request.method=="POST":
        nom_partenaire=request.POST.get('nom_partenaire')
        rccm=request.POST.get('rccm')
        numero_ifu=request.POST.get('numero_ifu')
        matricule=request.POST.get('matricule')
        date_de_creation=request.POST.get('date_de_creation')
        email=request.POST.get('email')
        type_entreprise=request.POST.get('type_entreprise')
        telephone=request.POST.get('telephone')
        adresse_localisation=request.POST.get('adresse_localisation')
        responsable=request.POST.get('responsable')
        mail_responsable=request.POST.get('mail_responsable')
        telephone_responsable=request.POST.get('telephone_responsable')
        domaine_activite=request.POST.get('domaine_activite')
        
        partenaire=Partenaire(
            id=id,
            entreprise=entreprise,
            nom_partenaire=nom_partenaire,
            rccm=rccm,
            numero_ifu=numero_ifu,
            matricule=matricule,
            date_de_creation=date_de_creation,
            email=email,
            type_entreprise=type_entreprise,
            telephone_responsable=telephone_responsable,
            telephone=telephone,
            adresse_localisation=adresse_localisation,
            responsable=responsable,
            mail_responsable=mail_responsable,
            domaine_activite=domaine_activite
        )
        
        partenaire.save()
        
        if partenaire is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a fait la mise à jour des informtions de l'un de ses partenaires .")
        return redirect('entreprises-utilisateur')
    return redirect('entreprises-utilisateur')

@login_required
def entreprises_delete_partenaire_utilisateur(request,id):
    partenaire=Partenaire.objects.filter(id=id)
    partenaire.delete()
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a supprimée un partenaire de son entreprise")
    return redirect('entreprises-utilisateur')

#certification
@login_required
def entreprises_create_certification_utilisateur(request):
    startups=Entreprise.objects.filter(responsable=request.user)
    def check_startup_user(item):
        if len(item)>=1:
            return item[0]
        else:
            return None
            
    entreprise=check_startup_user(startups)
    if request.method=="POST":
        nom=request.POST.get('nom')
        numero_certification=request.POST.get('numero_certification')
        type=request.POST.get('type')
        date_delivrance=request.POST.get('date_delivrance')
        organisme=request.POST.get('organisme')
        
        certification=Certification(
            entreprise=entreprise,
            nom=nom,
            numero_certification=numero_certification,
            type=type,
            date_delivrance=date_delivrance,
            organisme=organisme
        )
        certification.save()
        if certification is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a ajouté une certification à son entreprise {entreprise.nom}.")
        return redirect('entreprises-utilisateur')
    return redirect('entreprises-utilisateur')


@login_required
def entreprises_update_certification_utilisateur(request,id):
    startups=Entreprise.objects.filter(responsable=request.user)
    def check_startup_user(item):
        if len(item)>=1:
            return item[0]
        else:
            return None
            
    entreprise=check_startup_user(startups)
    if request.method=="POST":
        nom=request.POST.get('nom')
        numero_certification=request.POST.get('numero_certification')
        type=request.POST.get('type')
        date_delivrance=request.POST.get('date_delivrance')
        organisme=request.POST.get('organisme')
        
        certification=Certification(
            id=id,
            entreprise=entreprise,
            nom=nom,
            numero_certification=numero_certification,
            type=type,
            date_delivrance=date_delivrance,
            organisme=organisme
        )
        certification.save()
        if certification is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a ajouté une certification à son entreprise {entreprise.nom}.")
        return redirect('entreprises-utilisateur')
    return redirect('entreprises-utilisateur')


@login_required
def entreprises_delete_certification_utilisateur(request,id):
    certification=Certification.objects.filter(id=id)
    certification.delete()
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a supprimée une certification de son entreprise")
    return redirect('entreprises-utilisateur')


@login_required
def entreprises_create_annexe_utilisateur(request):
    startups=Entreprise.objects.filter(responsable=request.user)
    def check_startup_user(item):
        if len(item)>=1:
            return item[0]
        else:
            return None
            
    entreprise=check_startup_user(startups)
    
    if request.method=="POST":
        denomination=request.POST.get('denomination',"")
        responsable=request.POST.get('responsable',"")
        date_creation=request.POST.get('date_creation','')
        localisation=request.POST.get('localisation','')
        domaine_activite=request.POST.get('domaine_activite',"")
        tel_responsable=request.POST.get('tel_responsable',"")
        mail_responsable=request.POST.get('mail_responsable',"")
        
        annexe=Annexe(
            denomination=denomination,
            responsable=responsable,
            date_creation=date_creation,
            localisation=localisation,
            domaine_activite=domaine_activite,
            tel_responsable=tel_responsable,
            mail_responsable=mail_responsable,
            entreprise=entreprise
        )
        
        annexe.save()
        
        if annexe is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a ajouté une annexe à son entreprise {entreprise.nom}")
        return redirect('entreprises-utilisateur')
    return redirect('entreprises-utilisateur')


@login_required
def entreprises_delete_annexe_utilisateur(request,id):
    annexe=Annexe.objects.filter(id=id)
    annexe.delete()
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a supprimée une annexe de son entreprise")
    return redirect('entreprises-utilisateur')




@login_required
def entreprises_update_annexe_utilisateur(request,id):
    startups=Entreprise.objects.filter(responsable=request.user)
    def check_startup_user(item):
        if len(item)>=1:
            return item[0]
        else:
            return None
            
    entreprise=check_startup_user(startups)
    
    if request.method=="POST":
        denomination=request.POST.get('denomination',"")
        responsable=request.POST.get('responsable',"")
        date_creation=request.POST.get('date_creation','')
        localisation=request.POST.get('localisation','')
        domaine_activite=request.POST.get('domaine_activite',"")
        tel_responsable=request.POST.get('tel_responsable',"")
        mail_responsable=request.POST.get('mail_responsable',"")
        
        annexe=Annexe(
            id=id,
            denomination=denomination,
            responsable=responsable,
            date_creation=date_creation,
            localisation=localisation,
            domaine_activite=domaine_activite,
            tel_responsable=tel_responsable,
            mail_responsable=mail_responsable,
            entreprise=entreprise
        )
        
        annexe.save()
        
        if annexe is not None:
            user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a modifié une annexe à son entreprise {entreprise.nom}")
        return redirect('entreprises-utilisateur')
    return redirect('entreprises-utilisateur')

#end





#Company detail user view
@login_required
def company_detail_utilisateur(request):
    
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a consulté la page de la liste des entreprises.")
    notifications=Notification.objects.filter(recipient=request.user) 
    nombre_total_notification=len(notifications)
    context={
         "user":request.user,
            "notifications":notifications,
            "nombre_total_notification":nombre_total_notification
    }
    return render(request,"account/utilisateur/compagny-datail.html",context)



#Distinctions users views
@login_required
def distinctions_utilisateur(request):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    
    
    
    #Distinctions
    def distinction_repartition():
        for item in Distinctions.objects.all():
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            print(item.nombre_homme)
            print(item.nombre_femme)
            item.save()
    distinction_repartition()


    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a consulté la page de la liste des entreprises.")
    notifications=Notification.objects.filter(recipient=request.user) 
    nombre_total_notification=len(notifications)
    top_entreprises=Entreprise.objects.all().order_by('-budget_rang')[:3]
    
    
    
    
    
    
    entrepreneurs_nommine=len(Distinctions.objects.all())
    
    distinctions=Distinctions.objects.all().order_by("-annee")
    
    nombre_homme=[i for i in top_entreprises if i.responsable.sexe=="M"]
    
    
    nombre_homme=len(nombre_homme)
    nombre_femme=[i for i in top_entreprises if i.responsable.sexe=="F"]
    nombre_femme=len(nombre_femme)
    
    
    if Distinctions.objects.first():
        femme_distinction=Distinctions.objects.first().nombre_femme
    else:
        femme_distinction=0
    
    if Distinctions.objects.first():
        homme_distinction=Distinctions.objects.first().nombre_homme
    else:
        homme_distinction=0
    
    context={
        "user":request.user,
        "notifications":notifications,
        "nombre_total_notification":nombre_total_notification,
        "nombre_distinction":entrepreneurs_nommine,
        "top_entreprises":top_entreprises,
        "nombre_femme":femme_distinction,
        "nombre_homme":homme_distinction,
        "entrepreneurs_nommine":len(Distinctions.objects.all()),
        "distinctions":distinctions,
        "nombre_honore":len(Distinctions.objects.filter(status="Entrepreneur de le honore")),
        "distinctionjson":json.dumps([DistinctionSerializer(item).data for item in Distinctions.objects.all()])
        
        
    }
    
    return render(request,"account/utilisateur/distinctions.html",context)




#Entrepreneur user view
@login_required
def entrpreneurs_utilisateur(request):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()
    entreprises=Entreprise.objects.filter(responsable=request.user)
    def check_startup_user(item):
        if len(item)>=1:
            return item[0]
        else:
            return None
            
    entreprise=check_startup_user(entreprises)
    if request.method == 'POST':
        #user info
        photo=request.FILES.get('photo',"")
        promotion=request.POST.get('promotion',"")
        lieu_de_residence=request.POST.get('lieu_de_residence',"")
        date_inscription=request.POST.get("date_inscription","")
        telephone=request.POST.get('telephone',"")
        date_naissance=request.POST.get('date_naissance',"")
        sexe=request.POST.get('sexe',"")
        last_name=request.POST.get('last_name')
        first_name=request.POST.get('first_name')
        password=request.POST.get("password")
        email=request.POST.get('email')
        
        if not promotion:
            promotion=None
            
        if not lieu_de_residence:
            lieu_de_residence=None
            
        if not date_naissance:
            date_naissance=None
        if not date_inscription:
            date_inscription=timezone.now()
            
        if not photo:
            photo=None
            
        if not telephone:
            telephone=None
        if not sexe:
            sexe=None
        if lieu_de_residence=="":
            lieu_de_residence=None  
        
        user_category="utilisateur"
        
        #company info
        description=request.POST.get('description',"")
        nombre_employe=request.POST.get('nombre_employe',"")
        adresse_localisation=request.POST.get('adresse_localisation',"")
        domaine_activite=request.POST.get('domaine_activite',"")
        type=request.POST.get("type","")
        telephon=request.POST.get('telephon',"")
        mail=request.POST.get('mail',"")
        date_creation=request.POST.get('date_creation','')
        matricule=request.POST.get('matricule',"")
        num_ifu=request.POST.get('num_ifu','')
        rccm=request.POST.get('rccm','')
        nom=request.POST.get('nom','')
        whatsapp=request.POST.get('whatsapp',"")
        logo=request.FILES.get('logo',"")
        specialite=request.POST.get('specialite',"")
        
        
        if not logo:
            logo=None
        #create user here
        entreprise_user=Entreprise(
                    id=entreprise.id,
                    description=description,
                    nombre_employe=nombre_employe,
                    adresse_localisation=adresse_localisation,
                    domaine_activite=domaine_activite,
                    type=type,
                    telephon=telephon,
                    mail=mail,
                    date_creation=date_creation,
                    matricule=matricule,
                    num_ifu=num_ifu,
                    rccm=rccm,
                    nom=nom,
                    whatsapp=whatsapp,
                    logo=logo,
                    responsable=request.user,
                    specialite=specialite
                )
        entreprise_user.save()
        if entreprise_user is not None:
            user=User.objects.get(id=request.user.id)
            
            user.first_name = first_name
            user.last_name = last_name
            user.email=email
            user.sexe=sexe
            user.user_category=user_category
            user.lieu_de_residence=lieu_de_residence
            user.date_naissance=date_naissance
            user.date_inscription=date_inscription
            user.telephone=telephone
            user.promotion=promotion
            user.photo=File(photo)
            # user.password=password
            user.set_password(password)
            user.save()
            # user_actions_logger.info(f"Utilisateur {user.first_name} {user.last_name} a fait la mise à jour de ses infortions.")
            # logout(request)
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a fait la mise à jour de ses informations et donc s'est réconnecté.")
                return redirect('entrepreneurs-utilisateur')
            return redirect(settings.LOGIN_URL)
            #return redirect('entrepreneurs-utilisateur') 
    notifications=Notification.objects.filter(recipient=request.user) 
    nombre_total_notification=len(notifications)
    context={'entreprises':entreprises,"entreprise":entreprise,"nombre_entreprise":len(entreprises),
             "user":request.user,
            "notifications":notifications,
            "nombre_total_notification":nombre_total_notification}
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a consulté la page de la liste des entreprises.")
    return render(request,"account/utilisateur/entrepreneurs.html",context)



#User detail user view
@login_required
def user_detail_utilisateur(request):
    def classement_valeur():
        entreprises_totals=Entreprise.objects.all()
        for item in entreprises_totals:
            item.budget_rang=item.budget_classement()
            item.chiffre_affaire=item.calculate_chiffre_affaire()
            item.total_depenses=item.calculate_depenses()
            item.nombre_femme=item.nombre_Femme()
            item.nombre_homme=item.nombre_Homme()
            item.save()
    classement_valeur()

    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a consulté la page de la liste des entreprises.")
    notifications=Notification.objects.filter(recipient=request.user) 
    nombre_total_notification=len(notifications)
    context={
         "user":request.user,
            "notifications":notifications,
            "nombre_total_notification":nombre_total_notification
    }
    return render(request,"account/utilisateur/user-detail.html",context)




#Logout user/admin here
@login_required
def logout_user(request):
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} s'est déconnecté.")
    logout(request)
    return redirect(settings.LOGIN_URL)


#Signup admin here 
def signup_page(request):
    if request.method == 'POST':
        photo=request.FILES.get('photo',"")
        promotion=request.POST.get('promotion',"")
        lieu_de_residence=request.POST.get('lieu_de_residence',"")
        date_inscription=request.POST.get("date_inscription","")
        telephone=request.POST.get('telephone',"")
        date_naissance=request.POST.get('date_naissance',"")
        sexe=request.POST.get('sexe',"")
        last_name=request.POST.get('last_name')
        first_name=request.POST.get('first_name')
        password=request.POST.get("password")
        email=request.POST.get('email')
        
        if not promotion:
            promotion=None
            
        if not lieu_de_residence:
            lieu_de_residence=None
            
        if not date_naissance:
            date_naissance=None
        if not date_inscription:
            date_inscription=timezone.now()
            
        if not photo:
            photo=None
            
        if not telephone:
            telephone=None
        if not sexe:
            sexe=None
            
        
        user_category="admin"
        user=User.objects.create_superuser(
            first_name = first_name,
            last_name = last_name,
            email=email,
            sexe=sexe,
            user_category=user_category,
            lieu_de_residence=lieu_de_residence,
            date_naissance=date_naissance,
            date_inscription=date_inscription,
            telephone=telephone,
            promotion=promotion,
            photo=photo,
            password=password
            )
        if user is not None:
               
                login(request, user)
                user_actions_logger.info(f"Utilisateur {user.first_name} {user.last_name} s'est inscrit.")
                if (request.user.user_category=="admin"):
                    return redirect(settings.LOGIN_REDIRECT_URL_ADMIN) 
                elif(request.user.user_category=="utilisateur"):
                    return redirect(settings.LOGIN_REDIRECT_URL_UTILISATEUR)
                else:
                    return redirect('logout') 
    
    return render(request, 'account/admin/inscription.html')



#Signup user here 
def signup_page_utilisateur(request):
    if request.method == 'POST':
        #user info
        photo=request.FILES.get('photo',"")
        promotion=request.POST.get('promotion',"")
        lieu_de_residence=request.POST.get('lieu_de_residence',"")
        date_inscription=request.POST.get("date_inscription","")
        telephone=request.POST.get('telephone',"")
        date_naissance=request.POST.get('date_naissance',"")
        sexe=request.POST.get('sexe',"")
        last_name=request.POST.get('last_name')
        first_name=request.POST.get('first_name')
        password=request.POST.get("password")
        email=request.POST.get('email')
        
        if not promotion:
            promotion=None
            
        if not lieu_de_residence:
            lieu_de_residence=None
            
        if not date_naissance:
            date_naissance=None
        if not date_inscription:
            date_inscription=timezone.now()
            
        if not photo:
            photo=None
            
        if not telephone:
            telephone=None
        if not sexe:
            sexe=None
            
        
        user_category="utilisateur"
        
        #company info
        description=request.POST.get('description',"")
        nombre_employe=request.POST.get('nombre_employe',"")
        adresse_localisation=request.POST.get('adresse_localisation',"")
        domaine_activite=request.POST.get('domaine_activite',"")
        type=request.POST.get("type","")
        telephon=request.POST.get('telephon',"")
        mail=request.POST.get('mail',"")
        date_creation=request.POST.get('date_creation','')
        matricule=request.POST.get('matricule',"")
        num_ifu=request.POST.get('num_ifu','')
        rccm=request.POST.get('rccm','')
        nom=request.POST.get('nom','')
        whatsapp=request.POST.get('whatsapp',"")
        logo=request.FILES.get('logo',"")
        specialite=request.POST.get('specialite',"")
        
        
        if not logo:
            logo=None
        #create user here
        user=User.objects.create_user(
            first_name = first_name,
            last_name = last_name,
            email=email,
            sexe=sexe,
            user_category=user_category,
            lieu_de_residence=lieu_de_residence,
            date_naissance=date_naissance,
            date_inscription=date_inscription,
            telephone=telephone,
            promotion=promotion,
            photo=photo,
            password=password
            )
        
        if user is not None:
                entreprise=Entreprise(
                    description=description,
                    nombre_employe=nombre_employe,
                    adresse_localisation=adresse_localisation,
                    domaine_activite=domaine_activite,
                    type=type,
                    telephon=telephon,
                    mail=mail,
                    date_creation=date_creation,
                    matricule=matricule,
                    num_ifu=num_ifu,
                    rccm=rccm,
                    nom=nom,
                    whatsapp=whatsapp,
                    logo=logo,
                    responsable=user,
                    specialite=specialite
                )
                entreprise.save()
                if entreprise is not None:
                    login(request, user)
                    user_actions_logger.info(f"Utilisateur {user.first_name} {user.last_name} s'est inscrit.")
                    if (request.user.user_category=="admin"):
                        return redirect(settings.LOGIN_REDIRECT_URL_ADMIN) 
                    elif(request.user.user_category=="utilisateur"):
                        return redirect(settings.LOGIN_REDIRECT_URL_UTILISATEUR)
                    else:
                        return redirect('logout')
                else:
                    return redirect('signup-page-utilisateur') 
    return render(request, 'account/utilisateur/inscription.html')




#logging history view 
@login_required
def user_actions_view(request):
    log_file_pattern = 'user_actions*.log'  
    log_files = glob.glob(log_file_pattern)
    log_entries = []
    user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} a consulté les logs.")
    for log_file_path in sorted(log_files, reverse=True): 
        with open(log_file_path, 'r') as log_file:
            log_contents = log_file.read()
            log_entries.append({'file': log_file_path, 'contents': log_contents})

    return render(request, 'account/logs_history.html', {'log_entries': log_entries})



#Login user/admin
def login_page(request):
    message = ''
    if request.user.is_authenticated:
        if (request.user.user_category=="admin"):
            return redirect(settings.LOGIN_REDIRECT_URL_ADMIN) 
        elif(request.user.user_category=="utilisateur"):
            return redirect(settings.LOGIN_REDIRECT_URL_UTILISATEUR)
        else:
            return redirect('logout') 
    if request.method == 'POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        
        user = authenticate(email=email, password=password)
        if user is not None:
                login(request, user)
                user_actions_logger.info(f"Utilisateur {request.user.first_name} {request.user.last_name} s'est connecté.")
                message = f'Bonjour, {user.get_full_name()}! Vous êtes connecté.'
                if (request.user.user_category=="admin"):
                    return redirect(settings.LOGIN_REDIRECT_URL_ADMIN) 
                elif(request.user.user_category=="utilisateur"):
                    return redirect(settings.LOGIN_REDIRECT_URL_UTILISATEUR)
                else:
                    return redirect('logout') 
                
        else:
            user_actions_logger.warn(f"Un inconnu a éssayé d'accéder à votre site web voici ses informations de logs: son email: {request.POST.get('email')} , son mot de passe: {request.POST.get('password')}")
            message = 'Identifiants invalides.'
    return render(request, 'account/admin/connexion.html', context={'message': message})