from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
import re


class PhoneNumberField(models.CharField):
    default_validators = [
        RegexValidator(
            regex=r"^\+254\d{9}$",
            message="Phone number must be in the format +254XXXXXXXXX",
        )
    ]

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 13  # Adjust based on the length of the phone number
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        # Assume the database only stores the digits after +254
        return "+" + value

    def to_python(self, value):
        if value is None:
            return value
        value = value.strip()
        if value.startswith("+254"):
            return value  # Return as is
        if value.startswith("0"):
            value = value[1:]  # Remove leading 0
        if value.startswith("7"):
            value = "254" + value  # Format to +254
        return "+254" + value  # Ensure it starts with +254

    def get_prep_value(self, value):
        if value is None:
            return value
        # Remove the +254 part to save only the unique part
        return value.lstrip("+254")  # Save only the digits
