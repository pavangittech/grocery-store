from django.urls import path
from .views import home, product_list, cart_detail, cart_add, cart_remove, process_payment, checkout, order_tracking, register_view,login_view, logout_view

urlpatterns = [
    path('', home, name='home'),
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path('products/', product_list, name='product_list'),
    path('cart/', cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', cart_remove, name='cart_remove'),
    path('checkout/', checkout, name='checkout'),
    path('process_payment/', process_payment, name='process_payment'),
    path('orders/', order_tracking, name='order_tracking'),
]
