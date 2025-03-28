from decimal import Decimal
from django.conf import settings
from .models import Product

class Cart:
    def __init__(self, request):
        """Initialize the cart"""
        self.session = request.session
        cart = self.session.get('cart')

        if not cart:
            cart = self.session['cart'] = {}

        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """Add a product to the cart or update its quantity"""
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}

        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def remove(self, product):
        """Remove a product from the cart"""
        product_id = str(product.id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        """Save changes to the session"""
        self.session.modified = True

    def __iter__(self):
        """Iterate through the cart and get products"""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def get_total_price(self):
        """Calculate total price of items in the cart"""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """Remove all items from the cart"""
        del self.session['cart']
        self.save()
