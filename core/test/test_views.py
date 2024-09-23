from django.test import TestCase
from django.urls import reverse
from core.models import Customer, Order
from core.forms import SignUpForm
from django.contrib.auth import get_user_model

class LoginUserViewTests(TestCase):
    def setUp(self):       
        self.customer = get_user_model().objects.create_user(
            email="customer@test.com", customer_code="CUST001"
        )
    def test_login_success(self):        
        response = self.client.post(
            reverse("login"),
            {
                "email": self.customer.email,
                "customer_code": self.customer.customer_code,
            },
        )
        self.assertRedirects(
            response, reverse("list_orders", kwargs={"customer_id": self.customer.id})
        )
    def test_login_failed(self):        
        response = self.client.post(
            reverse("login"),
            {"email": "wrongemail@test.com", "customer_code": "wrongcode"},
        )
        self.assertContains(response, "Ensure you have a valid account")


class RegisterUserViewTests(TestCase):
    def test_register_success(self):
        """Test that a valid registration redirects to the list orders page"""
        response = self.client.post(
            reverse("register"),
            {
                "email": "newuser@test.com",
                "customer_code": "Developer1",
                "phone_number": "+254715150322",
            },
        )
        self.assertRedirects(response, reverse("list_orders"))
    def test_register_failed(self):
        """Test that an invalid registration returns an error"""
        response = self.client.post(
            reverse("register"),
            {
                "email": "",
                "customer_code": "Developer1",
            },
        )
        self.assertContains(response, "Invalid form submission")


class CreateOrderViewTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create_user(
            email="customer@test.com", customer_code="Developer1"
        )
        self.client.force_login(self.customer)
    def test_create_order_success(self):
        """Test that a valid order creation redirects to the list orders page"""
        response = self.client.post(
            reverse("create_order"),
            {"item_to_order": "Laptop", "amount": 3000, "quantity": 1},
        )
        self.assertRedirects(
            response, reverse("list_orders", kwargs={"customer_id": self.customer.id})
        )
        self.assertTrue(
            Order.objects.filter(
                customer=self.customer, item_to_order="Laptop"
            ).exists()
        )
    def test_create_order_failed(self):
        """Test that an invalid order submission returns an error"""
        response = self.client.post(
            reverse("create_order"),
            {"item_to_order": "", "amount": 3000, "quantity": 1},
        )
        self.assertContains(response, "An error occurred while creating your order")


class ListOrdersByCustomerViewTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create_user(
            email="customer@test.com", customer_code="Developer1"
        )
        self.order = Order.objects.create(
            customer=self.customer, item_to_order="Laptop", amount=3000, quantity=1
        )
        self.client.force_login(self.customer)
    def test_list_orders(self):
        """Test that orders for a customer are listed on the page"""
        response = self.client.get(
            reverse("list_orders", kwargs={"customer_id": self.customer.id})
        )
        self.assertContains(response, self.order.item_to_order)
        self.assertContains(response, self.order.amount)
