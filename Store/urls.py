from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import profile_settings, wishlist_view, add_to_wishlist, remove_from_wishlist

urlpatterns = [
    # Home & Auth
    path('', views.home, name='home'),
    path("register/", views.register_view, name="register"),
    path('profile/', views.profile, name='profile'),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('profile/settings/', profile_settings, name='profile_settings'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('wishlist/', wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),

    # Cart
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),

    # Orders & Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('process_payment/', views.process_payment, name='process_payment'),
    # path('razorpay-payment/<int:order_id>/', views.razorpay_payment, name='razorpay_payment'),
    # path('stripe-payment/<int:order_id>/', views.stripe_payment, name='stripe_payment'),
    path('orders/', views.order_tracking, name='order_tracking'),
    path('order-history/', views.order_history, name='order_history'),

    # Payment Result
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_failed/', views.payment_failed, name='payment_failed'),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='store/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='store/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='store/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='store/password_reset_complete.html'), name='password_reset_complete'),
]
