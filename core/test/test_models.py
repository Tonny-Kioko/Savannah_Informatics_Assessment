from django.test import TestCase
from core.models import Customer, Order, Item
from uuid import uuid4


class CustomerModelTests(TestCase):

    def setUp(self):
        self.email = "testuser@example.com"
        self.phone_number = "+254715150317"
        self.customer_code = "Developer1"
        self.customer = Customer.objects.create_user(
            email=self.email,
            customer_code=self.customer_code,
            phone_number=self.phone_number,
        )

    def test_create_customer(self):
        self.assertEqual(self.customer.email, self.email)
        self.assertEqual(self.customer.customer_code, self.customer_code)
        self.assertEqual(self.customer.phone_number, self.phone_number)
        
        self.assertEqual(str(self.customer), self.email)

    def test_customer_str(self):
        """Test the string representation of the customer"""
        self.assertEqual(str(self.customer), self.customer.email)


class ItemModelTest(TestCase):

    def setUp(self):
        self.item = Item.objects.create(item="Laptop", unit="pcs", price=1000)

    def test_create_item(self):
        self.assertEqual(self.item.item, "Laptop")
        self.assertEqual(self.item.unit, "pcs")
        self.assertEqual(self.item.price, 1000)
        self.assertIsInstance(self.item.item_id, uuid4().__class__)

    def test_item_str(self):
        self.assertEqual(str(self.item), self.item.item)


class OrderModelTests(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create_user(
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
        """Test if an order is created successfully"""
        self.assertEqual(self.order.customer.email, "customer@example.com")
        self.assertEqual(self.order.item_to_order, "Laptop")
        self.assertEqual(self.order.amount, 3000)
        self.assertEqual(self.order.quantity, 2)

    def test_order_str(self):
        """Test the string representation of the order"""
        self.assertEqual(str(self.order), str(self.order.order_number))

    def test_order_status_default(self):
        """Test if the default order status is 'Pending'"""
        self.assertEqual(self.order.status, "Pending")
