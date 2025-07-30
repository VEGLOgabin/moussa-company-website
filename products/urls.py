from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name="default-home"),
    path('home/',views.home,name="home"),
    path('products/',views.products,name="products"),
    path('blog/',views.blog,name="blog"),
    path('about/',views.about,name="about"),
    # path('order/',views.order,name="order"),
    path('testimonials/',views.testimonials,name="testimonials"),
    path('contact/',views.contact,name="contact"),
    path('partners/',views.partners,name="partners"),
    path('login/',views.login_view,name="login"),
    path('register/',views.register,name="register"),
    path('profile/',views.profile,name="profile"),
    path('logout/',views.logout,name="logout"),


    # #Admin actions
    # path('index-admin/',views.index_admin,name="index-admin"),
    # path('entreprises-admin/',views.entreprises_admin,name="entreprises-admin"),
    # path('entreprises-update-admin/<int:id>/',views.entreprises_update_admin,name="entreprises-update-admin"),
    # path('entreprises-delete-admin/<int:id>/',views.entreprises_delete_admin,name="entreprises-delete-admin"),
    # path('entrepreneurs-admin/',views.entrepreneurs_admin,name="entrepreneurs-admin"),
    # path('entrepreneurs-delete-admin/<int:id>/',views.entrepreneurs_delete_admin,name="entrepreneurs-delete-admin"),
    # path('entrepreneurs-update-admin/<int:id>/',views.entrepreneurs_update_admin,name="entrepreneurs-update-admin"),
    # path('company-detail-admin/<int:id>/',views.company_detail_admin,name="company-detail-admin"),
    # path('company-create-activite-admin/<int:company_id>/',views.company_create_activite_admin,name="entreprises-create-activite-admin"),
    # path('company-update-activite-admin/<int:company_id>/<int:id>/',views.company_update_activite_admin,name="company-update-activite-admin"),
    # path('company-delete-activite-admin/<int:company_id>/<int:id>/',views.company_delete_activite_admin,name="company-delete-activite-admin"),
    # path('company-create-produits-admin/<int:company_id>/',views.company_create_produits_admin,name='company-create-produits-admin'),
    # path('company-update-produits-admin/<int:company_id>/<int:id>/',views.company_update_produits_admin,name='company-update-produits-admin'),
    # path('company-delete-produits-admin/<int:company_id>/<int:id>/',views.company_delete_produits_admin,name='company-delete-produits-admin'),
    # path('company-create-partenaire-admin/<int:company_id>/',views.company_create_partenaire_admin,name='company-create-partenaire-admin'),
    # path('company-update-partenaire-admin/<int:company_id>/<int:id>/',views.company_update_partenaire_admin,name='company-update-partenaire-admin'),
    # path('company-delete-partenaire-admin/<int:company_id>/<int:id>/',views.company_delete_partenaire_admin,name='company-delete-partenaire-admin'),
    # path('company-create-certification-admin/<int:company_id>/',views.company_create_certification_admin,name='company-create-certification-admin'),
    # path('company-update-certification-admin/<int:company_id>/<int:id>/',views.company_update_certification_admin,name='company-update-certification-admin'),
    # path('company-delete-certification-admin/<int:company_id>/<int:id>/',views.company_delete_certification_admin,name='company-delete-certification-admin'),
    
    # path('company-create-annexe-admin/<int:company_id>/',views.company_create_annexe_admin,name='company-create-annexe-admin'),
    # path('company-update-annexe-admin/<int:company_id>/<int:id>/',views.company_update_annexe_admin,name='company-update-annexe-admin'),
    # path('company-delete-annexe-admin/<int:company_id>/<int:id>/',views.company_delete_annexe_admin,name='company-delete-annexe-admin'),
    
    # path('user-detail-admin/',views.user_detail_admin,name="user-detail-admin"),
    # path('distinctions-admin/',views.distinctions_admin,name="distinctions-admin"),
    # #end users actions
    
    
    # #login logout signup user and admin
    # path('logout/',views.logout_user,name="logout"),
    # path('login/',views.login_page,name="login-page"),
    # path('signup/',views.signup_page,name="signup-page"),
    # path('signup-utilisateur/',views.signup_page_utilisateur,name="signup-page-utilisateur"),
    # #end login actions 
    # #
    # #start users actions
    # #Now utilisateur
    # path('user-detail-utilisateur/',views.user_detail_utilisateur,name="user-detail-utilisateur"),
    # path('index-utilisateur/',views.index_utilisateur,name='index-utilisateur'),
    # path('entreprises-utilisateur/',views.entreprises_utilisateur,name='entreprises-utilisateur'),
    # path('user-detail-utilisateur/',views.user_detail_utilisateur,name='user-detail-utilisateur'),
    # path('distinctions-utilisateur/',views.distinctions_utilisateur,name='distinctions-utilisateur'),
    # path('company-detail-utilisateur/',views.company_detail_utilisateur,name='company-detail-utilisateur'),
    # path('entrepreneurs-update-utilisateur/',views.entrpreneurs_utilisateur,name='entrepreneurs-utilisateur'),
    # path('entreprises-create-activite-utilisateur/',views.entreprises_create_activite_utilisateur,name="entreprises-create-activite-utilisateur"),
    # path('entreprises-update-activite-utilisateur/<int:id>/',views.entreprises_update_activite_utilisateur,name="entreprises-update-activite-utilisateur"),
    # path('entreprises-delete-activite-utilisateur/<int:id>/',views.entreprises_delete_activite_utilisateur,name="entreprises-delete-activite-utilisateur"),
    # path('entreprises-create-produits-utilisateur/',views.entreprises_create_produits_utilisateur,name='entreprises-create-produits-utilisateur'),
    # path('entreprises-update-produits-utilisateur/<int:id>/',views.entreprises_update_produits_utilisateur,name='entreprises-update-produits-utilisateur'),
    # path('entreprises-delete-produits-utilisateur/<int:id>/',views.entreprises_delete_produits_utilisateur,name='entreprises-delete-produits-utilisateur'),
    # path('entreprises-create-partenaire-utilisateur/',views.entreprises_create_partenaire_utilisateur,name='entreprises-create-partenaire-utilisateur'),
    # path('entreprises-update-partenaire-utilisateur/<int:id>/',views.entreprises_update_partenaire_utilisateur,name='entreprises-update-partenaire-utilisateur'),
    # path('entreprises-delete-partenaire-utilisateur/<int:id>/',views.entreprises_delete_partenaire_utilisateur,name='entreprises-delete-partenaire-utilisateur'),
    # path('entreprises-create-certification-utilisateur/',views.entreprises_create_certification_utilisateur,name='entreprises-create-certification-utilisateur'),
    # path('entreprises-update-certification-utilisateur/<int:id>/',views.entreprises_update_certification_utilisateur,name='entreprises-update-certification-utilisateur'),
    # path('entreprises-delete-certification-utilisateur/<int:id>/',views.entreprises_delete_certification_utilisateur,name='entreprises-delete-certification-utilisateur'),
    # path('entreprises-create-cannexe-utilisateur/',views.entreprises_create_annexe_utilisateur,name='entreprises-create-annexe-utilisateur'),
    # path('entreprises-update-annexe-utilisateur/<int:id>/',views.entreprises_update_annexe_utilisateur,name='entreprises-update-annexe-utilisateur'),
    # path('entreprises-delete-annexe-utilisateur/<int:id>/',views.entreprises_delete_annexe_utilisateur,name='entreprises-delete-annexe-utilisateur'),
    # #end users actions
]