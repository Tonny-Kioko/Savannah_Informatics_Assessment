from django.urls import path, include
from core import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.loginUser, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerUser, name="register"),
    path("orders/create/", views.createOrder, name="create_order"),
    path("orders/delete/<int:pk>/", views.deleteOrder, name="delete_order"),
    path(
        "orders/<int:customer_id>/",
        views.listOrdersByCustomer,
        name="list_orders",
    ),
]
