from django.urls import path
from .views import home, pagamento, menu, profile, login, history



urlpatterns = [
    path('', home, name='home'), 
    path('payment/', pagamento, name='payment'),
    path('menu/', menu, name='menu'),
    path('profile/', profile, name='profile'),
    path('login/', login, name='login'),
    path('history/', history, name='history'),
]