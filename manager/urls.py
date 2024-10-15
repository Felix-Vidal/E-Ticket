from django.urls import path
from manager.views import home,dashboard,validar,validarQR, validar_usuario,ticketUnico

urlpatterns = [
    path('', home), # home
    path('dashboard/', dashboard, name='dashboard'),
    path('validar/', validar, name='validar'),
    path('validarQR/<int:codigo>/', validarQR, name='validarQR'),
    path('validar_usuario/', validar_usuario, name='validar_usuario'),
    path('ticketUnico/', ticketUnico, name='ticketUnico'),
    

]