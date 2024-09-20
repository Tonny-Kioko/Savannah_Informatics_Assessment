from django.test import TestCase
from django.urls import reverse
from core.models import Customer, Order
from django.contrib.auth import get_user_model
from django.utils import timezone


class IntegrationTests(TestCase):
    def setUp(self):        
        self.customer = get_user_model().objects.create_user(
            email="customer@test.com",
            customer_code="Developer1",
        )

        self.order = Order.objects.create(
            customer=self.customer,
            item_to_order="Laptop",
            amount=3000,
            quantity=1,
            order_placed_at=timezone.now(),
        )
    def test_home_page(self):
        """Test home page URL and template rendering"""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_register_user_integration(self):
        """Test that a user can register, log in, and get redirected to the orders page"""
        response = self.client.post(
            reverse("register"),
            {
                "email": "newuser@test.com",
                "customer_code": "Developer1",
                "phone_number": "+254715150322",
            },
        )
        self.assertRedirects(response, reverse("list_orders"))
        # Check that user was created in the database
        self.assertTrue(Customer.objects.filter(email="newuser@test.com").exists())

    def test_login_user_integration(self):
        """Test that a user can log in and view the order listing page"""
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

    def test_create_order_integration(self):
        """Test that a user can log in, create an order, and see it on the order list"""
        # Log in first
        self.client.login(
            email=self.customer.email, customer_code=self.customer.customer_code
        )
        # Post a new order
        response = self.client.post(
            reverse("create_order"),
            {
                "item_to_order": "Smartphone",
                "amount": 1200,
                "quantity": 2,
            },
        )
        self.assertRedirects(
            response, reverse("list_orders", kwargs={"customer_id": self.customer.id})
        )
        # Ensure the order was created and visible in the list
        response = self.client.get(
            reverse("list_orders", kwargs={"customer_id": self.customer.id})
        )
        self.assertContains(response, "Smartphone")
        self.assertContains(response, "1200")

    def test_delete_order_integration(self):
        """Test that a logged-in user can delete an order and it gets removed from the list"""
        # Log in first
        self.client.login(
            email=self.customer.email, customer_code=self.customer.customer_code
        )
        # Send delete order request
        response = self.client.post(
            reverse("delete_order", kwargs={"pk": self.order.pk})
        )
        # Check that user is redirected to the orders list
        self.assertRedirects(
            response, reverse("list_orders", kwargs={"customer_id": self.customer.id})
        )

        # Ensure the order is no longer in the list
        response = self.client.get(
            reverse("list_orders", kwargs={"customer_id": self.customer.id})
        )
        self.assertNotContains(response, self.order.item_to_order)

    def test_list_orders_integration(self):
        """Test that logged-in users can view their orders"""
        # Log in first
        self.client.login(
            email=self.customer.email, customer_code=self.customer.customer_code
        )
        # Check that the order list shows the correct orders for the logged-in customer
        response = self.client.get(
            reverse("list_orders", kwargs={"customer_id": self.customer.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.item_to_order)
        self.assertContains(response, self.order.amount)
