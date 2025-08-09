from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    # path('home/',views.home,name="home"),
    path('products/',views.products,name="products"),
    path('products/add/',views.add_product,name="add_product"),
    path('blog/',views.blog,name="blog"),
    path('about/',views.about,name="about"),
    path('payment-history/', views.payment_history, name='payment_history'),
    path('testimonials/',views.testimonials,name="testimonials"),
    path('contact/',views.contact,name="contact"),
    path('partners/',views.partners,name="partners"),
    path('login/',views.login_view,name="login"),
    path('register/',views.register,name="register"),
    path('profile/',views.profile,name="profile"),
    path('logout/',views.logout,name="logout"),
    
    
    
    
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    
    path('checkout/', views.checkout, name='checkout'),
    path('payment/notify/', views.payment_notify, name='payment_notify'),
    path('payment/return/', views.payment_return, name='payment_return'),
]