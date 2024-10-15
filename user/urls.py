from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import home, pagamento, menu, profile, login, history, aumentar_credito, manage



urlpatterns = [
    path('', home, name='home'), 
    path('aumentar-credito/', aumentar_credito, name='aumentar-credito'),
    path('payment/', pagamento, name='payment'),
    path('menu/', menu, name='menu'),
    path('profile/', profile, name='profile'),
    path('login/', login, name='login'),
    path('history/', history, name='history'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('manageUser/', manage, name='manage'), 
]