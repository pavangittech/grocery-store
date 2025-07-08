from django.test import TestCase
from .models import Product

class ProductModelTest(TestCase):
    def setUp(self):
        Product.objects.create(name="Tomato", price=10, stock=20)

    def test_product_created(self):
        tomato = Product.objects.get(name="Tomato")
        self.assertEqual(tomato.price, 10)
