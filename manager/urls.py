from django.urls import path
from manager.views import home,dashboard,validar

urlpatterns = [
    path('', home), # home
    path('dashboard/', dashboard, name='dashboard'),
    path('validar/', validar, name='validar'),

]