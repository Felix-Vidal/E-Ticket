from django.urls import path
from manager.views import home,dashboard,validar,validarQR,ticketUnico,relatorio, cardapio

urlpatterns = [
    path('', home), # home
    path('dashboard/', dashboard, name='dashboard'),
    path('validar/', validar, name='validar'),
    path('validarQR/<int:codigo>/', validarQR, name='validarQR'),
    path('ticketUnico/', ticketUnico, name='ticketUnico'),
    path('relatorio/', relatorio, name='relatorio'),
    path('cardapio/', cardapio, name='cardapio'),
    

]