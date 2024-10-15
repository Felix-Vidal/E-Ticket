from django.urls import path
from manager.views import home,dashboard,validar,validarQR, validar_usuario,ticketUnico,relatorio, cardapio
from manager.views import home,dashboard,validar,validarQR,vender,vendaUnico,usuarioCompra,relatorio, cardapio

urlpatterns = [
    path('', home), # home
    path('dashboard/', dashboard, name='dashboard'),
    path('validar/', validar, name='validar'),
    path('validarQR/<int:codigo>/', validarQR, name='validarQR'),
    path('validar_usuario/', validar_usuario, name='validar_usuario'),
    path('ticketUnico/', ticketUnico, name='ticketUnico'),
    path('relatorio/', relatorio, name='relatorio'),
    path('cardapio/', cardapio, name='cardapio'),
    path('ticketUnico/', ticketUnico, name='ticketUnico'),
    path('vender/', vender, name='vender'),    
    path('vendaUnico/', vendaUnico, name='vendaUnico'),  
    path('usuarioCompra/', usuarioCompra, name='usuarioCompra')
    

]