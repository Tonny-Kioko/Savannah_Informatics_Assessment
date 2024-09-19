import uuid
from .phone_number import PhoneNumberField
from django import forms
from core.models import Customer, Item, Order
from datetime import datetime
from django.contrib.auth import authenticate


class SignUpForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    phone_number = PhoneNumberField()
    customer_code = forms.CharField()

    class Meta:
        model = Customer
        fields = [            
            "email",
            "phone_number",
            "customer_code",
            
        ]
    def save(self, commit=True):

        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.customer_code = self.cleaned_data["customer_code"]

        user.last_login = datetime.now()
        if commit:
            user.save()
        return user


class UserSignInForm(forms.Form):
    email = forms.EmailField(required=True)
    customer_code = forms.CharField()


class OrderForm(forms.ModelForm):
    class Meta: 
        model = Order
        fields = [                      
            'item_to_order',
            'quantity',
            'amount', 
            'status',
        ]
