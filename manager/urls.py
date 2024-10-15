from django.urls import path
from manager.views import home,dashboard,validar,validarQR,vender,vendaUnico,usuarioCompra

urlpatterns = [
    path('', home), # home
    path('dashboard/', dashboard, name='dashboard'),
    path('validar/', validar, name='validar'),
    path('validarQR/', validarQR, name='validarQR'),
    path('vender/', vender, name='vender'),    
    path('vendaUnico/', vendaUnico, name='vendaUnico'),  
    path('usuarioCompra/', usuarioCompra, name='usuarioCompra')
    

]