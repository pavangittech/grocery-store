from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from .models import Product, Order, Payment, Wishlist
from .cart import Cart
from reportlab.pdfgen import canvas
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
import uuid

# Home
def home(request):
    return render(request, 'store/home.html')

# Profile Settings
@login_required
def profile_settings(request):
    return render(request, 'store/profile_settings.html', {'user': request.user})

# Product List View with Search, Category, Pagination
def product_list(request):
    products = Product.objects.all()
    query = request.GET.get("q")
    category = request.GET.get("category")

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
        messages.success(request, f"Showing results for '{query}'")

    if category:
        products = products.filter(category=category)
        messages.success(request, f"Filtered by category: {category.capitalize()}")

    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'store/product_list.html', {'products': products})

# Product Detail View
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

# Cart Views
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart})

def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product)
    return redirect('cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

@login_required
def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.add(product, quantity=quantity, update_quantity=True)
    return redirect('cart_detail')

# Wishlist Views
@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    messages.success(request, f"{product.name} added to wishlist.")
    return redirect('product_list')

@login_required
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    messages.info(request, "Removed from wishlist.")
    return redirect('wishlist')

# User Profile
@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/profile.html', {'orders': orders})

# Checkout
@login_required
def checkout(request):
    cart = Cart(request)
    return render(request, 'store/checkout.html', {'cart': cart})

@login_required
def process_payment(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        amount = float(request.POST.get("amount"))
        payment_method = request.POST.get("payment_method")

        order = Order.objects.create(
            user=request.user,
            total_amount=amount,
            status="Paid"
        )

        transaction_id = uuid.uuid4().hex

        Payment.objects.create(
            user=request.user,
            order=order,
            amount=amount,
            status="Success",
            transaction_id=transaction_id
        )

        return redirect("payment_success")

    return redirect("checkout")

# Payment Pages
def payment_success(request):
    return render(request, 'store/payment_success.html')

def payment_failed(request):
    return render(request, 'store/payment_failed.html')

# Orders & Invoices
@login_required
def order_tracking(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_tracking.html', {'orders': orders})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})

@login_required
def generate_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != "Delivered":
        return HttpResponse("Invoice is only available after delivery.")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=\"invoice_{order.id}.pdf\"'

    pdf = canvas.Canvas(response)
    pdf.setTitle(f"Invoice - Order {order.id}")
    pdf.drawString(100, 800, f"Invoice for Order ID: {order.id}")
    pdf.drawString(100, 780, f"Customer: {order.user.username}")
    pdf.drawString(100, 760, f"Total Amount: ${order.total_amount}")
    pdf.drawString(100, 740, f"Status: {order.status}")
    pdf.drawString(100, 720, f"Placed On: {order.created_at}")
    pdf.showPage()
    pdf.save()

    return response

# Auth Views
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "store/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = LoginForm()
    return render(request, "store/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("home")
