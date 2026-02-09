from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_POST
from .models import Product, Order, Testimonial, Partner, ContactMessage, BlogPost, PaymentHistory, OrderProduct, ProductRating, NewsletterSubscriber
from accounts.models import User
import logging
from django.utils import timezone
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import json
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import UserActionLog
from django.db import transaction
import uuid
from kkiapay import Kkiapay
# views.py - Add admin registration function
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from django.db import models
# Add this to your views.py
from django.db.models import Sum, Count
from datetime import datetime, timedelta



def log_user_action(request, action, level="INFO"):
    user = request.user if request.user.is_authenticated else None
    ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR"))
    user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")

    UserActionLog.objects.create(
        user=user,
        action=action,
        level=level,
        ip_address=ip,
        user_agent=user_agent
    )



def home(request):
    # Get featured products (you can add a 'featured' field to Product model later)
    featured_products = Product.objects.all()[:8]
    
    # Get latest products for new arrivals
    new_arrivals = Product.objects.order_by('-created_at')[:6]
    
    # Get best sellers (you can add ordering logic later)
    best_sellers = Product.objects.all()[:6]
    
    # Get latest blog posts
    latest_posts = BlogPost.objects.order_by('-published_at')[:3]
    
    context = {
        'user': request.user,
        'is_admin': request.user.is_authenticated and request.user.is_admin(),
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'testimonials': Testimonial.objects.all()[:4],
        'blogs': latest_posts,
        'partners': Partner.objects.all()[:8]
    }
    return render(request, "products/home.html", context)









# # # Product listing
def products(request):
    cart = request.session.get('cart', {})
    cart_product_ids = list(cart.keys())
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '')
    
    # Start with all products
    products_list = Product.objects.all()
    
    # Apply search filter
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Apply sorting
    if sort_by == 'name':
        products_list = products_list.order_by('name')
    elif sort_by == 'price_asc':
        products_list = products_list.order_by('price')
    elif sort_by == 'price_desc':
        products_list = products_list.order_by('-price')
    elif sort_by == 'newest':
        products_list = products_list.order_by('-created_at')
    else:
        products_list = products_list.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products_list, 9)
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    context = {
        'products': products_page,
        'is_admin': request.user.is_authenticated and request.user.is_admin(),
        'cart_product_ids': cart_product_ids,
        'search_query': search_query,  # Pass search back to template
        'sort_by': sort_by,            # Pass sort back to template
    }
    return render(request, "products/produits.html", context)





@require_POST
def add_to_cart_ajax(request, product_id):
    log_user_action(request, f"Add to cart called for product {product_id} ; Headers: {request.headers}")
    log_user_action(request, f"")
    
    # Remove the XMLHttpRequest check or make it optional
    try:
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        
        if product_id_str in cart:
            cart[product_id_str] += 1
        else:
            cart[product_id_str] = 1
            
        request.session['cart'] = cart
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'message': 'Produit ajouté au panier avec succès!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@require_POST
def remove_from_cart_ajax(request, product_id):
    # Remove the XMLHttpRequest check or make it optional
    try:
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        
        if product_id_str in cart:
            del cart[product_id_str]
            request.session['cart'] = cart
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'cart_count': len(cart),
                'message': 'Produit retiré du panier'
            })
        else:
            return JsonResponse({'success': False, 'message': 'Produit non trouvé dans le panier'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    
    


@login_required
def add_product(request):
    if request.method == 'POST':
        # if request.user.user_type != 'admin':
        #     messages.error(request, "Vous n'avez pas la permission d'ajouter un produit.")
        #     return redirect('products')

        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        available = request.POST.get('available', 0)
        currency = request.POST.get('currency', 'FCFA')
        image = request.FILES.get('image')

        try:
            Product.objects.create(
                name=name,
                description=description,
                price=price,
                available=available,
                currency=currency,
                image=image,
                added_by=request.user
            )
            messages.success(request, "Produit ajouté avec succès.")
        except Exception as e:
            print("Erreur lors de la création du produit:", e)
            messages.error(request, "Erreur lors de la création du produit.")
    return redirect('products')






@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.available = request.POST.get("available")
        product.currency = request.POST.get("currency", "FCFA")

        # If a new image is uploaded, delete the old one
        if request.FILES.get('image'):
            if product.image and os.path.isfile(product.image.path):
                os.remove(product.image.path)  # Delete old image file
            product.image = request.FILES.get('image')

        product.save()

    return redirect('products')






@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Remove product image from media folder if it exists
    if product.image and os.path.isfile(product.image.path):
        os.remove(product.image.path)

    product.delete()
    return redirect('products')






def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Get related products (same category or same seller, adjust as needed)
    related_products = Product.objects.filter(
        added_by=product.added_by
    ).exclude(id=product.id)[:4]
    
    # Get ratings for this product
    ratings = product.ratings.all().select_related('user')
    
    # Check if user has already rated this product
    user_rating = None
    user_rating_obj = None
    if request.user.is_authenticated:
        try:
            user_rating_obj = product.ratings.get(user=request.user)
            user_rating = user_rating_obj.rating
        except ProductRating.DoesNotExist:
            pass
    
    context = {
        'product': product,
        'is_admin': request.user.is_authenticated and request.user.is_admin(),
        'related_products': related_products,
        'ratings': ratings,
        'user_rating': user_rating,
        'user_rating_obj': user_rating_obj,
        'cart_product_ids': list(request.session.get('cart', {}).keys()),
    }
    
    return render(request, 'products/product_detail.html', context)

@login_required
def rate_product(request, product_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product = get_object_or_404(Product, id=product_id)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        
        if not rating:
            return JsonResponse({'success': False, 'error': 'Rating is required'})
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Invalid rating value'})
        
        # Update or create rating
        rating_obj, created = ProductRating.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                'rating': rating,
                'comment': comment if comment else None
            }
        )
        
        # Return updated product rating data
        return JsonResponse({
            'success': True,
            'average_rating': product.average_rating(),
            'rating_count': product.rating_count(),
            'user_rating': rating,
            'created': created,
            'message': 'Rating submitted successfully!' if created else 'Rating updated successfully!'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def delete_rating(request, product_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product = get_object_or_404(Product, id=product_id)
        
        try:
            rating = product.ratings.get(user=request.user)
            rating.delete()
            
            return JsonResponse({
                'success': True,
                'average_rating': product.average_rating(),
                'rating_count': product.rating_count(),
                'message': 'Rating deleted successfully!'
            })
        except ProductRating.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Rating not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})














@login_required
def payment_success(request):
    transaction_id = request.GET.get("transaction_id")
    try:
        order = Order.objects.get(transaction_id=transaction_id)
        order.status = "processing"  # or "paid" if you prefer
        order.save()

        # Save payment record
        PaymentHistory.objects.create(
            user=request.user,
            order=order,
            amount=order.total_price,
            transaction_id=transaction_id,
            status='success'
        )

        # Clear cart
        request.session['cart'] = {}

        messages.success(request, f"Paiement de {order.total_price} FCFA réussi !")
    except Order.DoesNotExist:
        messages.error(request, "Commande introuvable.")

    return redirect('products')  # or wherever you want to redirect after success



# About

def about(request):
    context = {
        'is_admin': request.user.is_authenticated and request.user.is_admin(),
    }
    return render(request, "products/about.html", context)

# Blog
def blog(request):
    context  = {
        "posts": BlogPost.objects.all(),
        'is_admin': request.user.is_authenticated and request.user.is_admin(),
        "user": request.user
        }
    return render(request, "products/blog.html", context)




import os

from django.utils.text import slugify

@login_required
def create_blog_post(request):
    """
    Handles the creation of a new blog post.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        cover_image = request.FILES.get('cover_image')
        
        # Automatically generate a unique slug from the title
        slug = slugify(title)
        
        try:
            # Check if a post with the same slug already exists
            if BlogPost.objects.filter(slug=slug).exists():
                # Append a unique identifier to the slug if it already exists
                original_slug = slug
                count = 1
                while BlogPost.objects.filter(slug=slug).exists():
                    slug = f"{original_slug}-{count}"
                    count += 1

            BlogPost.objects.create(
                posted_by=request.user,
                title=title,
                slug=slug,
                content=content,
                cover_image=cover_image
            )
            messages.success(request, "Article de blog créé avec succès.")
        except Exception as e:
            print("Erreur lors de la création de l'article de blog:", e)
            messages.error(request, "Erreur lors de la création de l'article de blog.")
    
    return redirect('blog') # Make sure you have a 'blog' URL name for the list page




def blog_detail(request, post_slug):
    """
    Displays a single blog post based on its slug.
    """
    # Use get_object_or_404 to handle cases where the slug doesn't match a post,
    # returning a standard 404 page instead of a server error.
    blog_post = get_object_or_404(BlogPost, slug=post_slug)

    # The context dictionary passes the blog_post object to the template
    context = {
        'blog_post': blog_post,
        'is_admin': request.user.is_authenticated and request.user.is_admin(),
    }
    return render(request, 'products/blog_detail.html', context)




@login_required
def update_blog_post(request, post_id):
    """
    Handles the updating of an existing blog post.
    """
    blog_post = get_object_or_404(BlogPost, id=post_id)

    # Optional: Add a check to ensure only the owner can edit the post
    if blog_post.posted_by != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à modifier cet article.")
        return redirect('blog')

    if request.method == 'POST':
        blog_post.title = request.POST.get('title')
        blog_post.content = request.POST.get('content')
        
        # Re-generate the slug in case the title has changed
        blog_post.slug = slugify(blog_post.title)

        # Handle new image upload
        new_image = request.FILES.get('cover_image')
        if new_image:
            # Delete old image if it exists
            if blog_post.cover_image and os.path.isfile(blog_post.cover_image.path):
                os.remove(blog_post.cover_image.path)
            blog_post.cover_image = new_image

        blog_post.save()
        messages.success(request, "Article de blog mis à jour avec succès.")
    
    return redirect('blog')

@login_required
def delete_blog_post(request, post_id):
    """
    Handles the deletion of a blog post.
    """
    blog_post = get_object_or_404(BlogPost, id=post_id)

    # Optional: Add a check to ensure only the owner can delete the post
    if blog_post.posted_by != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cet article.")
        return redirect('blog')

    if request.method == 'POST':
        # Delete image file from media folder if it exists
        if blog_post.cover_image and os.path.isfile(blog_post.cover_image.path):
            os.remove(blog_post.cover_image.path)
        
        blog_post.delete()
        messages.success(request, "Article de blog supprimé avec succès.")
    
    return redirect('blog')







# ----------------------
# TESTIMONIALS
# ----------------------

def testimonials(request):
    return render(request, "products/testimonials.html", {
        "testimonials": Testimonial.objects.all(),
    })

@login_required
def create_testimonial(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        content = request.POST.get('content')
        photo = request.FILES.get('photo')

        try:
            Testimonial.objects.create(
                name=name,
                content=content,
                photo=photo
            )
            messages.success(request, "Témoignage créé avec succès.")
        except Exception as e:
            print("Erreur lors de la création du témoignage:", e)
            messages.error(request, "Erreur lors de la création du témoignage.")
        
        return redirect('testimonials')

    return redirect('testimonials')


@login_required
def update_testimonial(request, testimonial_id):
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)

    if request.method == 'POST':
        testimonial.name = request.POST.get('name')
        testimonial.content = request.POST.get('content')

        new_photo = request.FILES.get('photo')
        if new_photo:
            if testimonial.photo and os.path.isfile(testimonial.photo.path):
                os.remove(testimonial.photo.path)
            testimonial.photo = new_photo
        
        testimonial.save()
        messages.success(request, "Témoignage mis à jour avec succès.")
        return redirect('testimonials')

    return redirect('testimonials')


@login_required
def delete_testimonial(request, testimonial_id):
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)

    if request.method == 'POST':
        if testimonial.photo and os.path.isfile(testimonial.photo.path):
            os.remove(testimonial.photo.path)
        testimonial.delete()
        messages.success(request, "Témoignage supprimé avec succès.")
        return redirect('testimonials')

    return redirect('testimonials')

# ----------------------
# PARTNERS
# ----------------------

def partners(request):
    return render(request, "products/partners.html", {
        "partners": Partner.objects.all(),
    })

@login_required
def create_partner(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        logo = request.FILES.get('logo')
        website = request.POST.get('website')

        try:
            Partner.objects.create(
                added_by=request.user,
                name=name,
                logo=logo,
                website=website
            )
            messages.success(request, "Partenaire ajouté avec succès.")
        except Exception as e:
            print("Erreur lors de l'ajout du partenaire:", e)
            messages.error(request, "Erreur lors de l'ajout du partenaire.")
        
        return redirect('partners')

    return redirect('partners')


@login_required
def update_partner(request, partner_id):
    partner = get_object_or_404(Partner, id=partner_id)

    # Optional: restrict edit to owner
    if partner.added_by != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à modifier ce partenaire.")
        return redirect('partners')

    if request.method == 'POST':
        partner.name = request.POST.get('name')
        partner.website = request.POST.get('website')

        new_logo = request.FILES.get('logo')
        if new_logo:
            if partner.logo and os.path.isfile(partner.logo.path):
                os.remove(partner.logo.path)
            partner.logo = new_logo
        
        partner.save()
        messages.success(request, "Partenaire mis à jour avec succès.")
        return redirect('partners')

    return redirect('partners')


@login_required
def delete_partner(request, partner_id):
    partner = get_object_or_404(Partner, id=partner_id)

    if partner.added_by != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer ce partenaire.")
        return redirect('partners')

    if request.method == 'POST':
        if partner.logo and os.path.isfile(partner.logo.path):
            os.remove(partner.logo.path)
        partner.delete()
        messages.success(request, "Partenaire supprimé avec succès.")
        return redirect('partners')

    return redirect('partners')






# Render the contact form page
def contact(request):
    return render(request, "products/contact.html")

# List all contact messages (for admin or staff)
@login_required
def contact_messages(request):
    messages_list = ContactMessage.objects.all()
    return render(request, "products/contact_messages.html", {"messages": messages_list})

# Create a new contact message (usually via a public contact form)
def create_contact_message(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')

        try:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_text
            )
            messages.success(request, "Votre message a été envoyé avec succès.")
        except Exception as e:
            print("Erreur lors de l'envoi du message:", e)
            messages.error(request, "Erreur lors de l'envoi du message.")
        return redirect('contact')

    # If GET, just redirect or render the contact page
    return redirect('contact')








# Update a contact message (usually restricted to admin)
@login_required
def update_contact_message(request, message_id):
    contact_msg = get_object_or_404(ContactMessage, id=message_id)

    if request.method == 'POST':
        contact_msg.name = request.POST.get('name')
        contact_msg.email = request.POST.get('email')
        contact_msg.subject = request.POST.get('subject')
        contact_msg.message = request.POST.get('message')
        contact_msg.save()
        messages.success(request, "Message mis à jour avec succès.")
        return redirect('contact_messages')

    return redirect('contact_messages')

# Delete a contact message (usually restricted to admin)
@login_required
def delete_contact_message(request, message_id):
    contact_msg = get_object_or_404(ContactMessage, id=message_id)

    if request.method == 'POST':
        contact_msg.delete()
        messages.success(request, "Message supprimé avec succès.")
        return redirect('contact_messages')

    return redirect('contact_messages')





@login_required
def payment_history(request):
    
    # # First, delete all pending payment records for this user
    # PaymentHistory.objects.filter(user=request.user, status='pending').delete()
    
    
    
    payments = PaymentHistory.objects.filter(user=request.user).order_by('-payment_date')
    
    # Calculate statistics
    total_payments = payments.count()
    successful_payments = payments.filter(status='success').count()
    pending_payments = payments.filter(status='pending').count()
    failed_payments = payments.filter(status='failed').count()
    
    # Calculate total amount spent (only successful payments)
    total_amount_spent = payments.filter(status='success').aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    
    # Get currency from first successful payment or default to FCFA
    currency = "FCFA"
    successful_payment = payments.filter(status='success').first()
    if successful_payment:
        currency = successful_payment.order.currency
    
    context = {
        'payments': payments,
        'is_admin': request.user.is_authenticated and request.user.is_admin(),
        'total_payments': total_payments,
        'successful_payments': successful_payments,
        'pending_payments': pending_payments,
        'failed_payments': failed_payments,
        'total_amount_spent': total_amount_spent,
        'currency': currency,
    }
    
    return render(request, 'products/payment_history.html', context)



@login_required
@require_POST
def delete_pending_payment(request, payment_id):
    """Delete a pending payment and its associated order"""
    try:
        payment = PaymentHistory.objects.get(id=payment_id, user=request.user)
        
        # Only allow deletion of pending payments
        if payment.status != 'pending':
            return JsonResponse({
                'success': False, 
                'message': 'Seuls les paiements en attente peuvent être supprimés.'
            })
        
        # Delete the associated order and payment
        order = payment.order
        payment.delete()
        order.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Paiement en attente supprimé avec succès.'
        })
        
    except PaymentHistory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Paiement non trouvé.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la suppression: {str(e)}'
        })


# Authentication

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        sex = request.POST.get('sex')
        birthdate = request.POST.get('birthdate')
        photo = request.FILES.get('photo')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email déjà utilisé")
            return redirect('register')

        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            phone_number=phone_number,
            sex=sex,
            birthdate=birthdate,
            photo=photo
        )
        login(request, user)
        return redirect('home')
    return render(request, 'products/register.html')





# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         user = authenticate(request, email=email, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('home')
#         else:
#             messages.error(request, 'Identifiants invalides')
#             return redirect('login')
#     return render(request, 'products/login.html')

# Updated login_view with user type redirection
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            
            # Redirect based on user type
            if user.user_type in ['admin', 'superadmin', 'manager']:
                # Admin users go to admin dashboard
                messages.success(request, f'Bienvenue Administrateur {user.first_name}!')
                return redirect('admin_dashboard')
            else:
                # Regular customers go to home
                messages.success(request, f'Bienvenue {user.first_name}!')
                return redirect('home')
        else:
            messages.error(request, 'Identifiants invalides')
            return redirect('login')
    
    return render(request, 'products/login.html')




def logout_view(request):
    logout(request)
    return redirect('home')





@login_required
def profile(request):
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.phone_number = request.POST.get('phone_number')
        request.user.sex = request.POST.get('sex')
        request.user.birthdate = request.POST.get('birthdate')
        if request.FILES.get('photo'):
            if request.user.photo and os.path.isfile(request.user.photo.path):
                os.remove(request.user.photo.path)  # Delete old photo file
            request.user.photo = request.FILES.get('photo')
        request.user.save()
        messages.success(request, 'Profil mis à jour.')
        return redirect('profile')
    context = {
        'user': request.user, 
        'is_admin': request.user.is_authenticated and request.user.is_admin(),
    }
    return render(request, 'products/profile.html', context)








from django.shortcuts import redirect
from django.contrib import messages
from products.models import Product







def cart_view(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = []
    total = 0

    for product in products:
        quantity = cart[str(product.id)]
        subtotal = quantity * product.price
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(request, 'products/cart.html', {
        'cart_items': cart_items,
        'total': total
    })
    
    

import json

@login_required
def update_cart_item(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        product = get_object_or_404(Product, pk=product_id)

        try:
            data = json.loads(request.body)
            qty = int(data.get('quantity', 1))
            if qty < 1:
                qty = 1
        except (ValueError, json.JSONDecodeError):
            qty = 1
        
        cart[str(product_id)] = qty
        request.session['cart'] = cart

        subtotal = product.price * qty
        total = sum(Product.objects.get(pk=int(k)).price * v for k, v in cart.items())

        return JsonResponse({
            'success': True,
            'quantity': qty,
            'subtotal': subtotal,
            'total': total
        })
    return JsonResponse({'success': False}, status=400)








def add_to_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        if product_id_str in cart:
            cart[product_id_str] += 1
        else:
            cart[product_id_str] = 1
        request.session['cart'] = cart
        messages.success(request, "Produit ajouté au panier.")
    return redirect('products')



# Remove from cart
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid_str = str(product_id)
    if pid_str in cart:
        del cart[pid_str]
        request.session['cart'] = cart
        messages.success(request, "Produit retiré du panier.")
    return redirect('products')





### LAST VERSION OF CHECKOUT WITH INTERNAL TRANSACTION ID AND ATOMIC ORDER/PAYMENT CREATION
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Votre panier est vide.")
        return redirect('marketplace')

    products = Product.objects.filter(id__in=cart.keys())
    cart_items = []
    total = 0

    for product in products:
        quantity = cart.get(str(product.id), 1)
        subtotal = product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
        total += subtotal

    # Generate unique INTERNAL transaction ID using UUID for safety
    internal_transaction_id = f"ORDER-{uuid.uuid4()}"

    # Create Order and PaymentHistory atomically
    with transaction.atomic():
        order = Order.objects.create(
            ordered_by=request.user,
            total_price=total,
            currency="FCFA",
            status="pending",
            internal_transaction_id=internal_transaction_id
        )

        # Create OrderProduct entries
        for item in cart_items:
            OrderProduct.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity']
            )

        # Create pending PaymentHistory record
        PaymentHistory.objects.create(
            user=request.user,
            order=order,
            amount=order.total_price,
            internal_transaction_id=internal_transaction_id,
            status='pending',
            payment_method='MOMO'
        )

    context = {
        "cart_items": cart_items,
        'is_admin': request.user.is_authenticated and request.user.is_admin(),
        "total": total,
        "order": order,
        "internal_transaction_id": internal_transaction_id,
        "timestamp": int(timezone.now().timestamp()),
        "public_key": settings.KKIAPAY_PUBLIC_KEY,
        "user": request.user,
        "callbackUrl": request.build_absolute_uri("/payment/callback/"),
    }

    return render(request, "products/checkout.html", context)



@csrf_exempt
def kkiapay_callback(request):
    """
    Handle KKIAPAY callback by verifying transaction server-side
    """
    kkiapay_transaction_id = request.GET.get('transaction_id')
    
    print("Transaction ID from callback:", kkiapay_transaction_id)

    if not kkiapay_transaction_id:
        messages.error(request, "Callback invalide : aucun ID de transaction.")
        return redirect('products')

    # Verify transaction directly with KKIAPAY
    kkiapay = Kkiapay(
        settings.KKIAPAY_PUBLIC_KEY,
        settings.KKIAPAY_PRIVATE_KEY,
        settings.KKIAPAY_SECRET_KEY,
        sandbox=True
    )
    
    try:
        transaction_info = kkiapay.verify_transaction(kkiapay_transaction_id)
        print("Transaction info from KKIAPAY:", transaction_info)
    except Exception as e:
        print("Error verifying transaction:", e)
        messages.error(request, "Impossible de vérifier la transaction.")
        return redirect('products')

    # Extract internal ID from 'state' instead of 'data'
    internal_transaction_id = transaction_info.get('state')
    print("Internal transaction ID from KKIAPAY:", internal_transaction_id)

    if not internal_transaction_id:
        messages.error(request, "Impossible de récupérer l'ID interne de la commande.")
        return redirect('products')

    # Now process the payment
    return handle_payment_success(request, kkiapay_transaction_id, internal_transaction_id)




def handle_payment_success(request, kkiapay_transaction_id, internal_transaction_id):
    """
    Verify KKIAPAY transaction and update order/payment safely.
    """
    from kkiapay import Kkiapay

    try:
        payment = PaymentHistory.objects.get(
            internal_transaction_id=internal_transaction_id
        )

        # Skip if payment already marked as success
        if payment.status == "success":
            return redirect('order_confirmation', order_id=payment.order.id)

        # Set status to processing
        payment.status = "processing"
        payment.save()

        # Verify with KKIAPAY
        kkiapay = Kkiapay(
            settings.KKIAPAY_PUBLIC_KEY,
            settings.KKIAPAY_PRIVATE_KEY,
            settings.KKIAPAY_SECRET_KEY,
            sandbox=True
        )
        transaction_info = kkiapay.verify_transaction(kkiapay_transaction_id)

        with transaction.atomic():
            order = payment.order
            if transaction_info.get("status") == "SUCCESS":
                payment.status = "success"
                order.status = "paid"
                messages.success(request, f"Paiement de {order.total_price} FCFA réussi !")
                # Clear cart
                if request.user.is_authenticated:
                    request.session['cart'] = {}
                    request.session.modified = True
            else:
                payment.status = "failed"
                messages.error(request, "Le paiement a échoué. Veuillez réessayer.")

            # Store KKIAPAY transaction ID
            payment.kkiapay_transaction_id = kkiapay_transaction_id
            payment.save()

            order.save()

        return redirect('order_confirmation', order_id=order.id)

    except PaymentHistory.DoesNotExist:
        messages.error(request, "Historique de paiement introuvable.")
        return redirect('products')
    except Order.DoesNotExist:
        messages.error(request, "Commande introuvable.")
        return redirect('products')
    except Exception as e:
        print(f"Erreur lors du traitement du paiement: {e}")
        messages.error(request, "Erreur lors du traitement du paiement.")
        return redirect('products')



def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.user.is_authenticated and order.ordered_by != request.user:
        messages.error(request, "Vous n'avez pas accès à cette commande.")
        return redirect('products')

    order_products = order.order_products.all()

    context = {
        'order': order,
        'is_admin': request.user.is_authenticated and request.user.is_admin(),
        'order_products': order_products,
    }
    return render(request, 'products/order_confirmation.html', context)




















###  ADMIN MANAGEMENT SESSION



def admin_check(user):
    """Check if user is admin/superadmin"""
    return user.is_authenticated and user.is_superuser

@login_required
# @user_passes_test(admin_check, login_url='login')
def admin_register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        admin_role = request.POST.get('admin_role')
        department = request.POST.get('department', '')
        
        # Admin-specific permissions
        can_manage_users = request.POST.get('can_manage_users') == 'on'
        can_manage_products = request.POST.get('can_manage_products') == 'on'
        can_manage_orders = request.POST.get('can_manage_orders') == 'on'
        
        # Optional fields
        sex = request.POST.get('sex', '')
        birthdate = request.POST.get('birthdate', None)
        photo = request.FILES.get('photo')

        # Validation
        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé par un administrateur")
            return redirect('admin_register')

        # Determine user_type based on admin_role
        user_type = 'manager'  # Default for admin roles
        
        if admin_role == 'superadmin':
            user_type = 'superadmin'
        elif admin_role in ['content', 'order', 'support']:
            user_type = 'admin'

        try:
            # Create admin user with elevated permissions
            admin_user = User.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                phone_number=phone_number,
                sex=sex,
                birthdate=birthdate,
                photo=photo,
                user_type=user_type,
                admin_role=admin_role,
                department=department,
                can_manage_users=can_manage_users,
                can_manage_products=can_manage_products,
                can_manage_orders=can_manage_orders,
                is_staff=True  # Admin users have staff access
            )
            
            messages.success(request, f"Administrateur {first_name} {last_name} créé avec succès!")
            return redirect('admin_dashboard')  # Or wherever you want to redirect
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la création: {str(e)}")
            return redirect('admin_register')
    
    return render(request, 'products/admin_register.html')





@login_required
# @user_passes_test(admin_check, login_url='login')
def admin_dashboard(request):
    # Get statistics
    user_count = User.objects.count()
    product_count = Product.objects.count()
    order_count = Order.objects.count()
    
    # Calculate total revenue (sum of all paid orders)
    total_revenue = Order.objects.filter(status='paid').aggregate(
        total=Sum('total_price')
    )['total'] or 0
    
    # Get recent orders (last 10)
    recent_orders = Order.objects.select_related('ordered_by').order_by('-ordered_at')[:10]
    
    # Get recent products (last 10)
    recent_products = Product.objects.select_related('added_by').order_by('-created_at')[:10]
    
    # Get recent activity from logs
    recent_activity = UserActionLog.objects.select_related('user').order_by('-created_at')[:15]
    
    # Format activity for template
    formatted_activity = []
    for activity in recent_activity:
        formatted_activity.append({
            'type': get_activity_type(activity.action),
            'icon': get_activity_icon(activity.action),
            'title': get_activity_title(activity.action),
            'description': activity.action,
            'time': format_activity_time(activity.created_at)
        })
    
    context = {
        'user_count': user_count,
        'is_admin': request.user.is_authenticated and request.user.is_admin(),
        'product_count': product_count,
        'order_count': order_count,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
        'recent_activity': formatted_activity,
    }
    
    return render(request, 'products/admin_dashboard.html', context)

def get_activity_type(action):
    """Determine activity type based on action content"""
    action_lower = action.lower()
    if any(word in action_lower for word in ['user', 'login', 'register', 'profile']):
        return 'user'
    elif any(word in action_lower for word in ['order', 'cart', 'checkout', 'payment']):
        return 'order'
    elif any(word in action_lower for word in ['product', 'create', 'update', 'delete']):
        return 'product'
    else:
        return 'payment'

def get_activity_icon(action):
    """Get appropriate icon for activity"""
    action_lower = action.lower()
    if any(word in action_lower for word in ['user', 'login', 'register']):
        return 'fa-user'
    elif any(word in action_lower for word in ['order', 'cart', 'checkout']):
        return 'fa-shopping-cart'
    elif any(word in action_lower for word in ['product', 'create', 'update', 'delete']):
        return 'fa-box'
    elif any(word in action_lower for word in ['payment', 'paid']):
        return 'fa-money-bill-wave'
    else:
        return 'fa-info-circle'

def get_activity_title(action):
    """Extract title from action"""
    words = action.split()
    if len(words) > 3:
        return ' '.join(words[:3]) + '...'
    return action

def format_activity_time(time):
    """Format time for display"""
    now = timezone.now()
    diff = now - time
    
    if diff.days > 7:
        return time.strftime("%d/%m/%Y")
    elif diff.days > 0:
        return f"{diff.days} jour(s) ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} heure(s) ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute(s) ago"
    else:
        return "À l'instant"
    
    
    
    

def newsletter_subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email")
        
        

        if email:
            email = email.strip()
            subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)

            if created:
                messages.success(request, "Merci pour votre abonnement 🎉")
            else:
                messages.info(request, "Vous êtes déjà abonné 😉")

        return redirect("home")
