from django.shortcuts import render, redirect
from .models import Product, Order, Payment, orderitem
from django.shortcuts import render, get_object_or_404, redirect
from .cart import Cart
import uuid
import stripe
import razorpay
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm

# Create your views here.
def home(request):
    return render(request, 'store/home.html')

def product_list(request):
    products = Product.objects.all()  # Fetch all products
    return render(request, 'store/product_list.html', {'products': products})

def cart_detail(request):
    """View to display cart details"""
    cart = Cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart})

def cart_add(request, product_id):
    """View to add product to cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product)
    return redirect('cart_detail')

def cart_remove(request, product_id):
    """View to remove product from cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')



def checkout(request):
    """Checkout page where user enters details"""
    cart = Cart(request)
    return render(request, 'store/checkout.html', {'cart': cart})

def process_payment(request):
    """Process payment after checkout form submission"""
    if request.method == "POST":
        name = request.POST['name']
        phone = request.POST['phone']
        amount = request.POST['amount']
        payment_method = request.POST['payment_method']

        order = Order.objects.create(user=request.user, total_amount=amount, status="Pending")

        transaction_id = uuid.uuid4().hex  # Generate unique transaction ID

        Payment.objects.create(order=order, transaction_id=transaction_id, amount=amount, payment_status="Pending")

        if payment_method == "stripe":
            return redirect("stripe_payment", order_id=order.id)
        elif payment_method == "razorpay":
            return redirect("razorpay_payment", order_id=order.id)
        elif payment_method == "paytm":
            return redirect("paytm_payment", order_id=order.id)
        elif payment_method == "phonepe":
            return redirect("phonepe_payment", order_id=order.id)
        elif payment_method == "gpay":
            return redirect("gpay_payment", order_id=order.id)

    return redirect("checkout")



stripe.api_key = "your_stripe_secret_key"

def stripe_payment(request, order_id):
    """Stripe payment processing"""
    order = Order.objects.get(id=order_id)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f'Order {order.id}',
                },
                'unit_amount': int(order.total_amount * 100),  # Convert to cents
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url="http://127.0.0.1:8000/payment_success/",
        cancel_url="http://127.0.0.1:8000/payment_failed/",
    )
    return JsonResponse({'session_id': session.id})



razorpay_client = razorpay.Client(auth=("your_key_id", "your_key_secret"))

def razorpay_payment(request, order_id):
    """Razorpay payment processing"""
    order = Order.objects.get(id=order_id)
    payment = razorpay_client.order.create({
        "amount": int(order.total_amount * 100),
        "currency": "INR",
        "payment_capture": 1,
    })
    return JsonResponse(payment)


def order_tracking(request):
    """Display user's order history and status"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_tracking.html', {'orders': orders})



def generate_invoice(request, order_id):
    """Generate a PDF invoice for a completed order"""
    order = Order.objects.get(id=order_id, user=request.user)

    if order.status != "Delivered":
        return HttpResponse("Invoice is only available after delivery.")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

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




@login_required
def process_payment(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        amount = request.POST.get("amount")
        payment_method = request.POST.get("payment_method")

        # Create an order
        order = Order.objects.create(
            user=request.user,
            total_amount=amount,
            status="Pending"
        )

        # Process payment (mock for now)
        transaction_id = "TXN123456"  # Replace this with actual transaction logic
        payment_status = "Success"  # Assume payment is successful for now

        # Create a payment record
        payment = Payment.objects.create(
            user=request.user,
            order=order,
            amount=amount,
            status=payment_status,  # Ensure this matches the Payment model
            transaction_id=transaction_id
        )

        # Update order status if payment succeeds
        if payment.status == "Success":
            order.status = "Paid"
            order.save()

        return redirect("order_tracking")  # Redirect to order tracking

    return redirect("cart_detail")




def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])  # Hash password
            user.save()
            login(request, user)  # Auto-login after registration
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "store/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "store/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("home")



@login_required
def add_product(request):
    # Your product addition logic
    pass



