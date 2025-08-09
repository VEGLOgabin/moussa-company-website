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


user_actions_logger = logging.getLogger('user_actions')



# Home page
def home(request):
    context = {
        'user': request.user,  # Optional: request.user is already available in templates
        'products': Product.objects.all(),
        'testimonials': Testimonial.objects.all(),
        'blogs': BlogPost.objects.order_by('-published_at')[:3],
        'partners': Partner.objects.all()
    }
    return render(request, "products/home.html", context)


# Product listing
def products(request):
    context = {
        'products': Product.objects.all(),
        'is_admin': request.user.is_authenticated and request.user.user_type == 'admin'
    }
    return render(request, "products/produits_1.html", context)


@login_required
def add_product(request):
    if request.method == 'POST':
        # if request.user.user_type != 'admin':
        #     messages.error(request, "Vous n'avez pas la permission d'ajouter un produit.")
        #     return redirect('products')

        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
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



@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST' and request.user.user_type == 'admin':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        product.save()
    return redirect('products')

@login_required
def delete_product(request, product_id):
    if request.user.user_type == 'admin':
        product = get_object_or_404(Product, id=product_id)
        product.delete()
    return redirect('products')





@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Votre panier est vide.")
        return redirect('products')

    products = Product.objects.filter(id__in=cart.keys())
    cart_items = []
    total = 0

    for product in products:
        quantity = cart[str(product.id)]
        subtotal = product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
        total += subtotal

    payment_error = None  # Will be passed to template

    if request.method == 'POST':
        order = Order.objects.create(
            ordered_by=request.user,
            total_price=total,
            currency="XOF",
            status='pending'
        )

        for item in cart_items:
            OrderProduct.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity']
            )

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
            payment_url = resp["data"]["payment_url"]
            request.session['cart'] = {}
            return redirect(payment_url)

    return render(request, 'products/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'payment_error': payment_error,  # Pass error to template
    })






# About

def about(request):
    context = {}
    return render(request, "products/about.html", context)

# Blog
def blog(request):
    return render(request, "products/blog.html", {"posts": BlogPost.objects.all()})

# Testimonials
def testimonials(request):
    return render(request, "products/temoignages.html", {"testimonials": Testimonial.objects.all()})

# Partners
def partners(request):
    return render(request, "products/partenaires.html", {"partners": Partner.objects.all()})





# Contact
def contact(request):
    return render(request, "products/contact.html")






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
            request.user.photo = request.FILES.get('photo')
        request.user.save()
        messages.success(request, 'Profil mis à jour.')
        return redirect('profile')
    context = {
        'user': request.user,  # optional, `request.user` is available by default
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

    return render(request, 'products/cart.html', {
        'cart_items': cart_items,
        'total': total
    })





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




