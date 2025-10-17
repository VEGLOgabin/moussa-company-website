from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_POST
from .models import Product, Order, Testimonial, Partner, ContactMessage, BlogPost, PaymentHistory, OrderProduct
from accounts.models import User
import logging
from .payment_utils import get_client
from django.utils import timezone
import os



user_actions_logger = logging.getLogger('user_actions')



# # Home page
# def home(request):
#     context = {
#         'user': request.user,
#         'products': Product.objects.all()[:6],
#         'testimonials': Testimonial.objects.all()[:6],
#         'blogs': BlogPost.objects.order_by('-published_at')[:6],
#         'partners': Partner.objects.all()
#     }
#     return render(request, "products/home.html", context)
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
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
        'testimonials': Testimonial.objects.all()[:4],
        'blogs': latest_posts,
        'partners': Partner.objects.all()[:8]
    }
    return render(request, "products/home.html", context)






# # Product listing
# def products(request):
    
#     cart = request.session.get('cart', {})
#     cart_product_ids = cart.keys()

#     context = {
#         'products': Product.objects.all(),
#         'is_admin': request.user.is_authenticated and request.user.user_type == 'admin',
#         'cart_product_ids': cart_product_ids
#     }
#     return render(request, "products/produits_3.html", context)

def products(request):
    cart = request.session.get('cart', {})
    cart_product_ids = list(cart.keys())  # keys are strings
    context = {
        'products': Product.objects.all(),
        # 'is_admin': request.user.is_authenticated and request.user.user_type == 'admin',
        'is_admin': True,
        'cart_product_ids': cart_product_ids
    }
    return render(request, "products/produits.html", context)




# from django.http import JsonResponse
# import json

# @require_POST
# def add_to_cart_ajax(request, product_id):
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         cart = request.session.get('cart', {})
#         product_id_str = str(product_id)
        
#         if product_id_str in cart:
#             cart[product_id_str] += 1
#         else:
#             cart[product_id_str] = 1
            
#         request.session['cart'] = cart
#         request.session.modified = True
        
#         return JsonResponse({
#             'success': True,
#             'cart_count': len(cart),
#             'message': 'Produit ajouté au panier avec succès!'
#         })
#     return JsonResponse({'success': False}, status=400)

# @require_POST
# def remove_from_cart_ajax(request, product_id):
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         cart = request.session.get('cart', {})
#         product_id_str = str(product_id)
        
#         if product_id_str in cart:
#             del cart[product_id_str]
#             request.session['cart'] = cart
#             request.session.modified = True
            
#             return JsonResponse({
#                 'success': True,
#                 'cart_count': len(cart),
#                 'message': 'Produit retiré du panier'
#             })
    
#     return JsonResponse({'success': False}, status=400)
from django.http import JsonResponse
import json

@require_POST
def add_to_cart_ajax(request, product_id):
    
    user_actions_logger.info(f"Add to cart called for product {product_id}")
    user_actions_logger.info(f"Headers: {request.headers}")
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
        quantity = request.POST.get('quantity', 1)
        currency = request.POST.get('currency', 'XOF')
        image = request.FILES.get('image')

        try:
            Product.objects.create(
                name=name,
                description=description,
                price=price,
                quantity=quantity,
                currency=currency,
                image=image,
                added_by=request.user
            )
            messages.success(request, "Produit ajouté avec succès.")
        except Exception as e:
            print("Erreur lors de la création du produit:", e)
            messages.error(request, "Erreur lors de la création du produit.")
    return redirect('products')



# @login_required
# def update_product(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     # if request.method == 'POST' and request.user.user_type == 'admin':
#     if request.method == 'POST':
#         product.name = request.POST.get('name')
#         product.description = request.POST.get('description')
#         product.price = request.POST.get('price')
#         if request.FILES.get('image'):
#             product.image = request.FILES.get('image')
#         product.save()
#     return redirect('products')


@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')

        # If a new image is uploaded, delete the old one
        if request.FILES.get('image'):
            if product.image and os.path.isfile(product.image.path):
                os.remove(product.image.path)  # Delete old image file
            product.image = request.FILES.get('image')

        product.save()

    return redirect('products')



# @login_required
# def delete_product(request, product_id):
#     # if request.user.user_type == 'admin':
#     if request.user.is_authenticated:
#         product = get_object_or_404(Product, id=product_id)
#         product.delete()
#     return redirect('products')



@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Remove product image from media folder if it exists
    if product.image and os.path.isfile(product.image.path):
        os.remove(product.image.path)

    product.delete()
    return redirect('products')





# @login_required
# def checkout(request):
#     cart = request.session.get('cart', {})
#     if not cart:
#         messages.error(request, "Votre panier est vide.")
#         return redirect('products')

#     products = Product.objects.filter(id__in=cart.keys())
#     cart_items = []
#     total = 0

#     for product in products:
#         quantity = cart[str(product.id)]
#         subtotal = product.price * quantity
#         cart_items.append({
#             'product': product,
#             'quantity': quantity,
#             'subtotal': subtotal
#         })
#         total += subtotal

#     payment_error = None  # Will be passed to template

#     if request.method == 'POST':
#         order = Order.objects.create(
#             ordered_by=request.user,
#             total_price=total,
#             currency="XOF",
#             status='pending'
#         )

#         for item in cart_items:
#             OrderProduct.objects.create(
#                 order=order,
#                 product=item['product'],
#                 quantity=item['quantity']
#             )

#         client = get_client()
#         transaction_id = f"ORDER-{order.pk}-{int(timezone.now().timestamp())}"
#         order.transaction_id = transaction_id
#         order.save()

#         data = {
#             "transaction_id": transaction_id,
#             "amount": int(order.total_price),
#             "currency": order.currency,
#             "description": f"Commande #{order.pk}",
#             "return_url": request.build_absolute_uri(reverse('payment_return')),
#             "notify_url": request.build_absolute_uri(reverse('payment_notify')),
#             "customer_name": request.user.first_name,
#             "customer_surname": request.user.last_name,
#             "customer_email": request.user.email,
#         }

#         resp = client.PaymentInitialization(data)
        
#         print(resp)

#         if not resp or resp.get("code") != "201":
#             error_message = resp.get("message", "Erreur inconnue")
#             error_description = resp.get("description", "")
#             payment_error = f"{error_message} - {error_description}"
#             messages.error(request, payment_error)
#         else:
#             payment_url = resp["data"]["payment_url"]
#             request.session['cart'] = {}
#             return redirect(payment_url)

#     return render(request, 'products/checkout.html', {
#         'cart_items': cart_items,
#         'total': total,
#         'payment_error': payment_error,  # Pass error to template
#     })



@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Votre panier est vide.")
        return redirect('products')

    # Fetch all products in the cart
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = []
    total = 0

    for product in products:
        quantity = cart.get(str(product.id), 1)  # session cart quantity
        subtotal = product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
        total += subtotal

    payment_error = None  # will be passed to template

    if request.method == 'POST':
        # Create the order
        order = Order.objects.create(
            ordered_by=request.user,
            total_price=total,
            currency="XOF",
            status='pending'
        )

        # Create OrderProduct entries
        for item in cart_items:
            OrderProduct.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity']
            )

        # Initialize payment
        client = get_client()
        transaction_id = f"ORDER-{order.pk}-{int(timezone.now().timestamp())}"
        order.transaction_id = transaction_id
        order.save()

        data = {
            "transaction_id": transaction_id,
            "amount": int(order.total_price),
            "currency": order.currency,
            "description": f"Commande #{order.pk}",
            "return_url": request.build_absolute_uri(reverse('payment_return')),
            "notify_url": request.build_absolute_uri(reverse('payment_notify')),
            "customer_name": request.user.first_name,
            "customer_surname": request.user.last_name,
            "customer_email": request.user.email,
        }

        resp = client.PaymentInitialization(data)
        print(resp)

        if not resp or resp.get("code") != "201":
            error_message = resp.get("message", "Erreur inconnue")
            error_description = resp.get("description", "")
            payment_error = f"{error_message} - {error_description}"
            messages.error(request, payment_error)
        else:
            # Clear cart only after successful payment initialization
            request.session['cart'] = {}
            return redirect(resp["data"]["payment_url"])

    return render(request, 'products/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'payment_error': payment_error,
    })



# About

def about(request):
    context = {}
    return render(request, "products/about.html", context)

# Blog
def blog(request):
    context  = {
        "posts": BlogPost.objects.all(),
        "user": request.user
        }
    return render(request, "products/blog_1_1.html", context)




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
    }
    return render(request, 'products/blog_detail_2.html', context)




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





# # Testimonials
# def testimonials(request):
#     return render(request, "products/temoignages.html", {"testimonials": Testimonial.objects.all()})

# # Partners
# def partners(request):
#     return render(request, "products/partenaires.html", {"partners": Partner.objects.all()})




# ----------------------
# TESTIMONIALS
# ----------------------

def testimonials(request):
    return render(request, "products/testimonials_1.html", {
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
    return render(request, "products/partners_1.html", {
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





# # Contact
# def contact(request):
#     return render(request, "products/contact.html")

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
    payments = PaymentHistory.objects.filter(user=request.user).order_by('-payment_date')
    return render(request, 'products/payment_history.html', {'payments': payments})




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





def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
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
    }
    return render(request, 'products/profile.html', context)








from django.shortcuts import redirect
from django.contrib import messages
from products.models import Product

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

    return render(request, 'products/cart_2.html', {
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





from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import PaymentHistory

@csrf_exempt
def payment_notify(request):
    trans_id = request.POST.get('cpm_trans_id')
    client = get_client()
    resp = client.TransactionVerfication_trx(trans_id)
    
    if resp.json.get("data", {}).get("status") == "ACCEPTED":
        order = Order.objects.filter(transaction_id=trans_id).first()
        if order:
            PaymentHistory.objects.get_or_create(
                order=order,
                defaults={
                    'user': order.ordered_by,
                    'amount': order.total_price,
                    'transaction_id': trans_id,
                    'status': 'success'
                }
            )
            order.status = 'processing'
            order.save()
    return HttpResponse(status=200)


def payment_return(request):
    trans_id = request.GET.get('transaction_id')
    client = get_client()
    resp = client.TransactionVerfication_trx(trans_id)

    status = resp.json.get("data", {}).get("status")
    if status == "ACCEPTED":
        messages.success(request, "Paiement réussi ! Merci pour votre commande.")
    else:
        messages.error(request, "Paiement échoué. Veuillez réessayer.")

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
