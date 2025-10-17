from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    # path('home/',views.home,name="home"),
    path('products/',views.products,name="products"),
    path('products/add/',views.add_product,name="add_product"),
    path('products/update/<int:product_id>/', views.update_product, name='update_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('cart/add/<int:product_id>/', views.add_to_cart_ajax, name='add_to_cart_ajax'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart_ajax, name='remove_from_cart_ajax'),
    
    
    path('blog/',views.blog,name="blog"),
    path("blog/post/", views.create_blog_post, name = "post_news"),
    path('blog/<slug:post_slug>/', views.blog_detail, name='blog_detail'),
    path("post/update/<int:post_id>/", views.update_blog_post, name="post_update"),
    path("post/delete/<int:post_id>/", views.delete_blog_post, name="post_delete"),



    path('about/',views.about,name="about"),
    
    
    path('testimonials/',views.testimonials,name="testimonials"),
    path('testimonials/add/',views.create_testimonial,name="testimonial_add"),
    path('testimonials/update/<int:testimonial_id>/',views.update_testimonial,name="testimonial_update"),
    path('testimonials/delete/<int:testimonial_id>/',views.delete_testimonial,name="testimonial_delete"),
        
    
    path('partners/',views.partners,name="partners"),
    path('partners/add/',views.create_partner,name="partner_add"),
    path('partners/update/<int:partner_id>/',views.update_partner,name="partner_update"),
    path('partners/delete/<int:partner_id>/',views.delete_partner,name="partner_delete"),
    
    
    
    
    path('contact/', views.contact, name='contact'),
    path('contact/messages/', views.contact_messages, name='contact_messages'),
    path('contact/messages/add/', views.create_contact_message, name='contact_message_add'),  # usually form POST from public page
    path('contact/messages/update/<int:message_id>/', views.update_contact_message, name='contact_message_update'),
    path('contact/messages/delete/<int:message_id>/', views.delete_contact_message, name='contact_message_delete'),
    
    
    
    
    path('login/',views.login_view,name="login"),
    path('register/',views.register,name="register"),
    path('profile/',views.profile,name="profile"),
    path('logout/',views.logout_view,name="logout"),
    
    
    
    
    # path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart_item, name='update_cart_item'),

    
    path('checkout/', views.checkout, name='checkout'),
    path('payment/notify/', views.payment_notify, name='payment_notify'),
    path('payment/return/', views.payment_return, name='payment_return'),
    path('payment-history/', views.payment_history, name='payment_history'),

]