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
        return "+254" + value.lstrip("0")

    def to_python(self, value):
        if value is None:
            return value
        value = value.strip()
        if value.startswith("+"):
            value = value[1:]
        if not value.startswith("254"):
            value = "254" + value
        return "+" + value

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if value is not None:
            if not re.match(r"^\+254\d{9}$", value):
                raise ValidationError(
                    "Phone number must be in the format +254XXXXXXXXX"
                )

    def get_prep_value(self, value):
        if value is None:
            return value
        return value.lstrip("+")
