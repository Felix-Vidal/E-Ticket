from django.urls import path
from user.views import home, pagamento, menu, profile, login



urlpatterns = [
    path('', home), # home
    path('payment/', pagamento),
    path('menu/', menu),
    path('profile/', profile),
    path('login/', login)
]