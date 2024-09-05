from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return render(request, 'user/pages/home.html')

def pagamento(request):
    return render(request,'user/pages/payment.html')

def menu(request):
    return render(request, 'user/pages/menu.html')

def profile(request):
    return render(request, 'user/pages/profile.html')

def login(request):
    return render(request, 'user/pages/login.html')






