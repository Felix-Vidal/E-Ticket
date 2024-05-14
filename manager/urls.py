from django.urls import path
from manager.views import home

urlpatterns = [
    path('', home), # home
]