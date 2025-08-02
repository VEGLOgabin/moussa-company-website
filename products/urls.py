from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    # path('home/',views.home,name="home"),
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
]