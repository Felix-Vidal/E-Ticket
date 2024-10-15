from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from user.models import PersonalData, MEAL_TYPES
from datetime import datetime
# Create your views here.

def home(request):
    return render(request, 'manager/pages/home.html')

def dashboard (request):
    return render(request, 'manager/pages/dashboard.html')

def validar (request):
    return render(request, 'manager/pages/validar.html')

def validarQR(request, codigo):  # Recebe o código como parâmetro
    if codigo:
        # Obtém os dados do usuário usando a matrícula
        personal_data = PersonalData.objects.get(registration_number=codigo)
        classifications = " / ".join(personal_data.classifications.values_list('name', flat=True))  # Junta as classificações
        
        current_hour = datetime.now().hour
        if 6 <= current_hour < 11:
            meal_type = 'BREAKFAST'
        elif 11 <= current_hour < 17:
            meal_type = 'LUNCH'
        else:
            meal_type = 'DINNER'
        meal_name = dict(MEAL_TYPES).get(meal_type)
        context = {
            'user_full_name': personal_data.full_name,
            'user_cpf': personal_data.cpf,
            'user_matricula': personal_data.registration_number,
            'user_balance': personal_data.credit,  # Certifique-se de ter um campo de saldo
            'user_unit': personal_data.unit,        # Adicione um campo de unidade
            'user_classifications': classifications,
            'meal_type': meal_name,
        }
        return render(request, 'manager/pages/validarQR.html', context)
    return render(request, 'manager/pages/validarQR.html')

def ticketUnico (request):
    return render(request, 'manager/pages/ticketUnico.html')