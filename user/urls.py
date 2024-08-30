from django.urls import path
from user.views import home, pagamento



urlpatterns = [
    path('', home), # home
    path('payment/', pagamento) 


]