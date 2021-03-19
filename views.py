from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect
from rest_framework.response import Response
from bike.forms import ReviewForm, SignupForm, SigninForm
from bike.models import Prod, Cate
from bike.serializer import ProductSerializer


def home(request):
    products = Prod.objects.filter(active=True)
    categories = Cate.objects.filter(active=True)
    context = {"products": products, "categories": categories}
    return render(request, "bike/home.html", context)


def search(request):
    q = request.GET["q"]
    products = Prod.objects.filter(active=True, name__icontains=q)
    categories = Cate.objects.filter(active=True)
    context = {"products": products,
               "categories": categories,
               "title": q + " - search"}
    return render(request, "bike/list.html", context)


def categories(request, slug):
    cat = Cate.objects.get(slug=slug)
    products = Prod.objects.filter(active=True, category=cat)
    categories = Cate.objects.filter(active=True)
    context = {"products":products, "categories":categories, "title":cat.name + " - Categories"}
    return render(request, "bike/list.html", context)


def detail(request, slug):
    product = Prod.objects.get(active=True, slug=slug)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Review is saved")
        else:
            messages.error(request, "Invalid Form")
    else:
        form = ReviewForm()
    categories = Cate.objects.filter(active=True)
    context = {"product" : product,
               "categories":categories,
               "form": form}
    return render(request, "bike/detail.html", context)


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            messages.success(request, "User saved")
            return redirect("bike:signin")
        else:
            messages.error(request, "Error in form")
    else:
        form = SignupForm()
    context = {"form": form}
    return render(request, "bike/signup.html", context)


def signin(request):
    if request.method=="POST":
        form = SigninForm(request.POST)
        # username = req.POST["username"]
        # password = req.POST["password"]
        username = form["username"].value()
        password = form["password"].value()
        user = authenticate(request, username=username,  password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully logged in")
            return redirect("bike:home")
        else:
            messages.error(request, "Invalid Username or Password")
    else:
        form = SigninForm()
    context = {"form": form}
    return render(request, "bike/signin.html", context)


def signout(request):
    logout(request)
    messages.success(request,"You have successfully logged out")
    return redirect("bike:home")


def cart(request, slug):
    product = Prod.objects.get(slug=slug)
    inital = {"items":[],"price":0.0,"count":0}
    session = request.session.get("data", inital)
    if slug in session["items"]:
        messages.error(request, "Already added to cart")
    else:
        session["items"].append(slug)
        session["price"] += float(product.price)
        session["count"] += 1
        request.session["data"] = session
        messages.success(request, "Added successfully")
    return redirect("bike:detail", slug)


def mycart(request):
    sess = request.session.get("data", {"items":[]})
    products = Prod.objects.filter(active=True, slug__in=sess["items"])
    categories = Cate.objects.filter(active=True)
    context = {"products": products,
               "categories": categories,
               "title": "My Cart"}
    return render(request, "bike/list.html", context)


def checkout(request):
    request.session.pop('data', None)
    return redirect("/")
