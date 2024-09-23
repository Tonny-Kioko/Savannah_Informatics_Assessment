from django.test import TestCase
from core.models import Customer, Order


class CustomerModelTests(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            email="testuser@example.com",
            phone_number="+254715150322",
            customer_code="Developer1",
        )
    def test_customer_creation(self):
        """Test if a customer is created successfully"""
        self.assertEqual(self.customer.email, "testuser@example.com")
        self.assertEqual(self.customer.customer_code, "Developer1")
    def test_customer_str(self):
        
        self.assertEqual(str(self.customer), self.customer.email)


class OrderModelTests(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            email="customer@example.com",
            phone_number="+254715150322",
            customer_code="Developer1",
        )

        self.order = Order.objects.create(
            customer=self.customer,
            item_to_order="Laptop",
            amount=3000,
            quantity=2,
            status="Pending",
        )
    def test_order_creation(self):        
        self.assertEqual(self.order.customer.email, "customer@example.com")
        self.assertEqual(self.order.item_to_order, "Laptop")
        self.assertEqual(self.order.amount, 3000)
        self.assertEqual(self.order.quantity, 2)

    def test_order_str(self):       
        self.assertEqual(str(self.order), str(self.order.order_number))

    def test_order_status_default(self):        
        self.assertEqual(self.order.status, "Pending")
