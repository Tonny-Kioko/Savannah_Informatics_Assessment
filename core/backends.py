from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model


class CustomerBackend(BaseBackend):
    def authenticate(self, request, email=None, customer_code=None):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email, customer_code=customer_code)
            return user
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
