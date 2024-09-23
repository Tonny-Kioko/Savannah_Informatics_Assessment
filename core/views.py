from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from jsonschema import ValidationError
from django.contrib.auth import get_backends
from django.contrib.auth.backends import ModelBackend
from core.models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login

from core.forms import SignUpForm, UserSignInForm, OrderForm
from core.send_confirmation import SendSms


def home(request):
    return render(request, "home.html")


def loginUser(request):
    if request.method == "POST":
        form = UserSignInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            customer_code = form.cleaned_data["customer_code"]

            user = authenticate(request, email=email, customer_code=customer_code)
            if user is not None:

                auth_login(
                    request, user
                )
                messages.success(request, "Customer Login Successful")
                print("User logged in")
                return redirect("list_orders", customer_id=request.user.id)
            else:
                messages.error(request, "Ensure you have a valid account")
                print("User authentication failed")
                return redirect("login")
    else:
        form = UserSignInForm()

    context = {"form": form}
    return render(request, "login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("home")


def registerUser(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.save()

            user = authenticate(
                request, email=user.email, customer_code=user.customer_code
            )
            if user is not None:
                login(
                    request,
                    user,
                    backend="core.authentication_backends.EmailCustomerCodeBackend",
                )
                messages.success(
                    request, "Registration successful, and you're now logged in."
                )
                return redirect("list_orders", customer_id=request.user.id)
            else:
                messages.error(request, "Registration failed. Please try again.")
                return redirect("register")
        else:
            messages.error(
                request,
                "Invalid form submission. Please correct the errors and try again.",
            )
    else:
        form = SignUpForm()

    context = {"form": form}
    return render(request, "register.html", context)


@login_required(login_url="login")
def createOrder(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)            
            order.customer = request.user 
            order.save()

            sms_sender = SendSms()
            sms_sender.sending(order, order.customer)

            messages.success(request, "Your order has been created.")
            
            return redirect("list_orders", customer_id=request.user.id)
        else:
            messages.error(request, "An error occurred while creating your order.")
    else:
        form = OrderForm()

    return render(request, "create_order.html", {"form": form})


@login_required(login_url="login")
def deleteOrder(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
      order.delete()
      messages.success(request, "Your Order has been deleted Successfully")
      return redirect('list_orders', customer_id=order.customer.id)
    return render (request, 'delete_order.html', {'order': order})


@login_required(login_url= 'login')
def listOrdersByCustomer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    orders = Order.objects.filter(customer=customer)
    context = {"orders": orders, "customer": customer}
    return render(request, "list_order.html", context)
