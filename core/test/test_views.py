from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Customer, Order


class ViewsTests(TestCase):
    def setUp(self):
        self.customer = get_user_model().objects.create_user(
            email="customer@test.com",
            customer_code="Developer1",
        )
        self.client.login(
            email=self.customer.email, customer_code=self.customer.customer_code
        )

    def test_home_page(self):
        """Test that the home page loads successfully."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_login_user_success(self):
        """Test that a user can log in successfully."""
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
        self.assertEqual(response.wsgi_request.user, self.customer)

    def test_login_user_failure(self):
        """Test that login fails with invalid credentials."""
        response = self.client.post(
            reverse("login"),
            {
                "email": "wrongemail@test.com",
                "customer_code": "wrongcode",
            },
        )
        self.assertEqual(
            response.status_code, 302
        ) 
        

    def test_register_user_success(self):
        """Test that a user can register successfully."""
        response = self.client.post(
            reverse("register"),
            {
                "email": "newuser@test.com",
                "customer_code": "Developer1",
                "phone_number": "+254715150322",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Customer.objects.filter(email="newuser@test.com").exists())

    def test_register_user_failure(self):
        """Test that registration fails with invalid data."""
        response = self.client.post(
            reverse("register"),
            {
                "email": "",
                "customer_code": "Developer1",
            },
        )
        self.assertEqual(response.status_code, 200)
        

    def test_create_order_success(self):
        """Test that a user can create an order successfully."""
        response = self.client.post(
            reverse("create_order"),
            {
                "item_to_order": "Laptop",
                "amount": 3000,
                "quantity": 1,
            },
        )
        self.assertEqual(response.status_code, 200)
        

    def test_create_order_failure(self):
        """Test that creating an order fails with invalid data."""
        response = self.client.post(
            reverse("create_order"),
            {
                "item_to_order": "",
                "amount": 3000,
                "quantity": 1,
            },
        )
        self.assertContains(response, "An error occurred while creating your order.")

    def test_delete_order_success(self):
        """Test that a user can delete an order successfully."""
        order = Order.objects.create(
            customer=self.customer, item_to_order="Laptop", amount=3000, quantity=1
        )

        response = self.client.post(reverse("delete_order", kwargs={"pk": order.pk}))
        self.assertRedirects(
            response, reverse("list_orders", kwargs={"customer_id": self.customer.id})
        )
        self.assertFalse(Order.objects.filter(pk=order.pk).exists())

    def test_list_orders_success(self):
        """Test that a user can view their orders."""
        order = Order.objects.create(
            customer=self.customer, item_to_order="Laptop", amount=3000, quantity=1
        )

        response = self.client.get(
            reverse("list_orders", kwargs={"customer_id": self.customer.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.item_to_order)
        self.assertContains(response, order.amount)
