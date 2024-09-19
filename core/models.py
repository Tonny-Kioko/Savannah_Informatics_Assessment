import uuid
from django.db import models
from .phone_number import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class Customer(AbstractBaseUser):
    email = models.EmailField(unique=True, blank=False)
    phone_number = PhoneNumberField(max_length=13)
    customer_code = models.CharField(max_length=100)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["customer_code"]

    def __str__(self):
        return self.email


class CustomerManager(BaseUserManager):
    def create_user(self, email, customer_code, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, customer_code=customer_code, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, customer_code, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, customer_code, **extra_fields)


class Item(models.Model):
    item_id = models.UUIDField(default=uuid.uuid4, editable=False)
    item = models.CharField(max_length=200)
    unit = models.CharField(max_length=200)
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name

STATUS = (
    ("Pending", "Pending"),    
    ("Order Complete", "Order Complete")
)

class Order(models.Model):
    order_number = models.UUIDField(default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    item_to_order = models.CharField(max_length=200)  
    amount = models.PositiveBigIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    order_placed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS, default="Pending", max_length=100)

    class Meta:
        ordering = ['-order_placed_at']

    def __str__(self):
        return f'{self.order_number}'
