from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home(request):
    return render(request, 'manager/pages/home.html')

def dashboard (request):
    return render(request, 'manager/pages/dashboard.html')

def validar (request):
    return render(request, 'manager/pages/validar.html')

def validarQR (request):
    return render(request, 'manager/pages/validarQR.html')

def vender (request):
    return render(request, 'manager/pages/vender.html')

def vendaUnico (request):
    return render(request, 'manager/pages/vendaUnico.html')

def usuarioCompra (request):
    return render(request, 'manager/pages/usuarioCompra.html')