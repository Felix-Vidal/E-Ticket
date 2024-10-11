from django.urls import path
from manager.views import home,dashboard,validar,validarQR

urlpatterns = [
    path('', home), # home
    path('dashboard/', dashboard, name='dashboard'),
    path('validar/', validar, name='validar'),
    path('validarQR/', validarQR, name='validarQR'),
    

]