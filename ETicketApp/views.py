from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages

from django.contrib.auth.decorators import user_passes_test, login_required 
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User, Group


from .models import *
import requests
from django.contrib.auth.hashers import check_password, make_password
from datetime import datetime, date
from io import BytesIO
import base64
import qrcode
from decimal import Decimal

# Create your views here.

@login_required
def home(request):
    # Obtém os dados pessoais do usuário logado
    personal_data = get_object_or_404(DadoPessoal, usuario=request.user)

    # Gera o QR Code a partir do número de matrícula
    qr_data = personal_data.matricula
    qr_img = qrcode.make(qr_data)

    # Salva a imagem em um buffer
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Passa os dados para o template
    context = {
        'credito': personal_data.credito,
        'matricula': personal_data.matricula,
        'qr_image': qr_image,
    }
    return render(request, 'ETicketApp/pages/user/home.html', context)

@login_required
def aumentar_credito(request):
    if request.method == 'POST':
        valor = request.POST.get('valor')
        if valor:
            try:
                valor_decimal = Decimal(valor)
                personal_data = get_object_or_404(DadoPessoal, usuario=request.user)
                personal_data.credito += valor_decimal
                personal_data.save()
                messages.success(request, 'Crédito aumentado com sucesso!')  # Mensagem de sucesso
                return redirect('home')  # Redireciona para a página inicial
            except (DadoPessoal.DoesNotExist, Decimal.InvalidOperation):
                messages.error(request, 'Falha ao aumentar crédito. Verifique o valor e tente novamente.')  # Mensagem de erro
                return redirect('home')  # Volta para a mesma página
    return redirect('home')

@login_required
def pagamento(request):
    return render(request,'ETicketApp/pages/user/pagamento.html')

@login_required
def menu(request):
    hoje = date.today()  # Obtém a data de hoje
    
    # Filtra um item para cada tipo de refeição no menu do dia
    cafe = Cardapio.objects.filter(data=hoje, tipo_refeicao="CAFE_DA_MANHA").first()
    almoco = Cardapio.objects.filter(data=hoje, tipo_refeicao="ALMOCO").first()
    jantar = Cardapio.objects.filter(data=hoje, tipo_refeicao="JANTAR").first()
    
    # Adiciona os menus ao contexto
    context = {
        'cafe': cafe,
        'almoco': almoco,
        'jantar': jantar,
    }
    
    return render(request, 'ETicketApp/pages/user/menu.html', context)

@login_required
def perfil(request):
    # Obtém o objeto DadoPessoal relacionado ao usuário logado
    personal_data = get_object_or_404(DadoPessoal, usuario=request.user)

    # Passa os dados do usuário e suas classificações para o template
    context = {
        'nome_completo': personal_data.nome_completo,
        'cpf': personal_data.cpf,
        'matricula': personal_data.matricula,
        'unidade': personal_data.unidade,
        'classificacoes': personal_data.classificacoes.all(),
    }
    
    return render(request, 'ETicketApp/pages/user/perfil.html', context)

# Defina a URL da API externa
UFAC_API_URL = "https://sistemas.ufac.br/api/csi/usuarios-ru/"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJzZWNyZXQiOiJROVlweEFMTndsRzJWbXlibTJWak4wY2dEcFhLRTMiLCJ0b2tlbiI6ImxFa2tBQTlhbTVianFwWTlzMWpLQzJOeXU1SWh5b01LTVBOS1huajFkRTNFRUNUcDQ1dmYzSmNOQ0pzQiIsInVzZXJuYW1lIjoiYWx1bm9zLXNpLWFwcC1ydSIsInBhc3N3b3JkIjoiUTlZcHhBTE53bEcyVm15Ym0yVmpOMGNnRHBYS0UzIiwiaWR1c2VyIjoiNSJ9.qZXjStlIV6g7BOiMSYg53oP4waIqkDnc63Ku10zpT3k"
def login(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        password = request.POST.get('password')

        if not cpf or not password:
            return render(request, 'ETicketApp/pages/user/login.html', {'error_message': 'CPF e senha são obrigatórios.'})

        try:
            # Tenta buscar o usuário localmente usando o CPF
            personal_data = DadoPessoal.objects.get(cpf=cpf)
            usuario = personal_data.usuario

            # Verifica se a senha está correta
            if check_password(password, usuario.password):
                auth_login(request, usuario) 
                return redirect('home')  # Redireciona para a página inicial

            else:
                return render(request, 'ETicketApp/pages/user/login.html', {'error_message': 'Senha incorreta.'})

        except DadoPessoal.DoesNotExist:
            # Se o CPF não existe localmente, fazer a requisição à API externa
            headers = {
                'Authorization': f'Bearer {BEARER_TOKEN}',
            }
            response = requests.post(UFAC_API_URL, json={"cpf": cpf}, headers=headers)
            
        
         
            if response.status_code == 200:
                external_data = response.json()

                if external_data['record_count'] == 0:
                    return render(request, 'ETicketApp/pages/user/login.html', {'error_message': 'Usuário não encontrado na API externa.'})

                # Acessa o primeiro registro da lista "response"
                for user_data in external_data['response']:
                    if user_data.get('SITUACAO') == 'Ativo': break

                # Extrai os dados do usuário
                matricula = user_data.get('MATRICULA')
                nome_completo = user_data.get('NOME')
                nome_social = user_data.get('NOME_SOCIAL')
                cpf = user_data.get('CPF')
                unit = user_data.get('UNIDADE')
                entry_date = user_data.get('DT_ENTRADA')
                nome_classificacao = user_data.get('CLASSIFICACAO')
                gratuitous = user_data.get('GRATUIDADE') == 'S'  # Converte 'S' ou 'N' para booleano

                # Busca ou cria uma classificação com base no nome retornado
                classification, created = Classificacao.objects.get_or_create(nome=nome_classificacao)

                # Cria um novo usuário localmente
                usuario = User.objects.create(
                    username=cpf,
                    password=make_password(password),  # Criptografa a senha
                )
                personal_data = DadoPessoal.objects.create(
                    usuario=usuario,
                    nome_completo=nome_completo,
                    nome_social=nome_social,
                    cpf=cpf,
                    matricula=matricula,
                    data_entrada=entry_date,
                    unidade=unit,
                    credito=0.0,  # Inicialmente, crédito zero
                    gratuito=gratuitous,
                )
                personal_data.classificacoes.add(classification)
                auth_login(request, usuario)
                return redirect('home')  # Redireciona para a página inicial após sucesso

            else:
                return render(request, 'ETicketApp/pages/user/login.html', {'error_message': 'Erro na API externa.'})

    return render(request, 'ETicketApp/pages/user/login.html')



@login_required
def historico(request):
    return render(request, 'ETicketApp/pages/user/historico.html')


# MANAGER


def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def dashboard (request):
    return render(request, 'ETicketApp/pages/manager/dashboard.html')

@user_passes_test(is_superuser)
def validar (request):
    return render(request, 'ETicketApp/pages/manager/validar.html')

@user_passes_test(is_superuser)
def validarUsuario(request):  # Recebe o código como parâmetro
    if request.method == 'POST':
        matricula = request.POST.get('matricula')
        # Obtém os dados do usuário usando a matrícula
        dados_pessoais = DadoPessoal.objects.get(matricula=matricula)
        classificacoes = " / ".join(dados_pessoais.classificacoes.values_list('nome', flat=True))  # Junta as classificações
        current_hour = datetime.now().hour
        if 6 <= current_hour < 10:
            meal_type = 1
        elif 10 <= current_hour < 17:
            meal_type = 2
        else:
            meal_type = 3
        nome_refeicao = TipoRefeicaoEnum.get_name_by_value(meal_type)
        context = {
            'nome_completo': dados_pessoais.nome_completo,
            'cpf': dados_pessoais.cpf,
            'matricula': dados_pessoais.matricula,
            'credito': dados_pessoais.credito,  # Certifique-se de ter um campo de saldo
            'unidade': dados_pessoais.unidade,        # Adicione um campo de unidade
            'classificacoes': classificacoes,
            'tipo_refeicao': nome_refeicao,
        }
        return render(request, 'ETicketApp/pages/manager/validarUsuario.html', context)
    return render(request, 'ETicketApp/pages/manager/validarUsuario.html')

@user_passes_test(is_superuser)
def validar_usuario(request):
    if request.method == 'POST':
        matricula = request.POST.get('matricula')
        tipo_refeicao = request.POST.get('tipo_refeicao')
        

        try:
            # Busca o usuário pela matrícula
            dados_pessoais = DadoPessoal.objects.get(matricula=matricula)

            # Se o usuário for gratuito, não deduz crédito
            if dados_pessoais.gratuito:
                messages.success(request, 'Usuário gratuito, refeição validada sem desconto de crédito.')

                # Registra a refeição gratuita
                Refeicao.objects.create(
                    usuario=dados_pessoais.usuario,
                    valor=0.00,
                    gratuito=True,
                    data=datetime.now().date(),
                    hora=datetime.now().time(),
                    menu=None  # Ou substitua isso com o cardápio adequado
                )

                return redirect('validar')  # Redireciona para /manage/validar/

            # Busca a classificação com a maior prioridade (menor valor de 'prioridade')
            classificacao = dados_pessoais.classificacoes.order_by('prioridade').first()

            if not classificacao:
                messages.error(request, 'Nenhuma classificação encontrada para o usuário.')
                return redirect('validar')

            # Calcula o valor da refeição com base no tipo de refeição
            if tipo_refeicao == 'CAFE_DA_MANHA':
                valor = classificacao.valor_cafe_manha
            elif tipo_refeicao == 'ALMOCO':
                valor = classificacao.valor_almoco
            elif tipo_refeicao == 'JANTAR':
                valor = classificacao.valor_jantar
            else:
                messages.error(request, 'Tipo de refeição inválido.')
                return redirect('validar')

            # Verifica se o usuário tem crédito suficiente
            if dados_pessoais.credito >= valor:
                # Deduz o valor da refeição do crédito do usuário
                dados_pessoais.credito -= valor
                dados_pessoais.save()

                # Registra a refeição
                Refeicao.objects.create(
                    usuario=dados_pessoais.usuario,
                    valor=valor,
                    gratuito=False,
                    data=datetime.now().date(),
                    hora=datetime.now().time(),
                    menu=Cardapio.objects.filter(data=datetime.now().date(), tipo_refeicao=tipo_refeicao).first()
                )

                messages.success(request, 'Refeição validada com sucesso!')
            else:
                messages.error(request, 'Crédito insuficiente para validar a refeição.')

        except DadoPessoal.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')

    return redirect('validar')

@user_passes_test(is_superuser)
def ticketUnico (request):
    return render(request, 'ETicketApp/pages/manager/ticketUnico.html')

@user_passes_test(is_superuser)
def relatorio (request):
    return render(request, 'ETicketApp/pages/manager/relatorio.html')

@user_passes_test(is_superuser)
def cardapio (request):
    return render(request, 'ETicketApp/pages/manager/cardapio.html')

def cardapioExterno (request):
    return render(request, 'ETicketApp/pages/manager/cardapioExterno.html')

def vender (request):
    return render(request, 'ETicketApp/pages/manager/vender.html')

def vendaUnico (request):
    return render(request, 'ETicketApp/pages/manager/vendaUnico.html')

def usuarioCompra (request):
    if request.method == 'POST':
        if request.POST.get('matricula'):
            matricula = request.POST.get('matricula')
            print(matricula)
            dados_pessoais = DadoPessoal.objects.get(matricula=matricula)
            context = {
                'nome_completo': dados_pessoais.nome_completo,
                'cpf': dados_pessoais.cpf,
                'matricula': dados_pessoais.matricula,
                'credito': dados_pessoais.credito,
                'unidade': dados_pessoais.unidade,
            }
            print(dados_pessoais)
            return render(request, 'ETicketApp/pages/manager/usuarioCompra.html', context)
        print(request.POST.get('valor'))
        if request.POST.get('valor'):
            valor = request.POST.get('valor')
            if valor:
                try:
                    valor_decimal = Decimal(valor)
                    personal_data = get_object_or_404(DadoPessoal, usuario=request.user)
                    personal_data.credito += valor_decimal
                    personal_data.save()
                    messages.success(request, 'Crédito aumentado com sucesso!')  # Mensagem de sucesso
                    return redirect('vender')  # Redireciona para a página inicial
                except (DadoPessoal.DoesNotExist, Decimal.InvalidOperation):
                    messages.error(request, 'Falha ao aumentar crédito. Verifique o valor e tente novamente.')  # Mensagem de erro
                    return redirect('vender')  # Volta para a mesma página
            
    print("terceiro")
    return render(request, 'ETicketApp/pages/manager/usuarioCompra.html')

def usuarios (request):
    usuarios = User.objects.filter(groups__isnull=False).distinct()


    # Passar os dados para o template
    context = {
        'usuarios': usuarios
    }
    return render(request, 'ETicketApp/pages/manager/usuarios.html', context)

def listar_usuarios_grupo(request):
    grupo_colaboradores = Group.objects.get(name="Colaboradores")  # Nome do grupo
    usuarios = grupo_colaboradores.user_set.all()  # Todos os usuários no grupo

    # Passar os usuários para o template
    context = {
        'usuarios': usuarios,
    }
    return render(request, 'ETicketApp/pages/manager/usuarios.html', context)

def add_usuario (request):
    return render(request, 'ETicketApp/pages/manager/add_user.html')

def gerenciar_usuario(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')  # O nome do campo de input no template
        papel = request.POST.get('papel')  # O ID do papel selecionado
        
        # Mapeamento de papéis
        papeis_dict = {
            '1': 'ADM',
            '2': 'Colaborador',
            '3': 'Bolsista'
        }

        try:
            user = User.objects.get(username=cpf)
            print(papel, papeis_dict)
            # Verifica se o papel é válido
            if papel in papeis_dict:
                # Remove o usuário de todos os grupos primeiro
                user.groups.clear()

                # Adicionar o usuário ao grupo selecionado
                grupo = Group.objects.get(name=papeis_dict[papel])
                print(grupo)
                user.groups.add(grupo)

                messages.success(request, f'{user.username} foi adicionado ao grupo {grupo.name} com sucesso.')
            else:
                messages.error(request, 'Papel inválido.')
        
        except User.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')

        return redirect('usuarios')  # Redireciona após a operação


def cadastro_cardapio(request):
    cardapio = Cardapio()
    cardapio.cafe = request.POST.get('cafe')
    cardapio.cafe_inicio = request.POST.get('hora-inicio-cafe')
    cardapio.cafe_inicio = request.POST.get('hora-final-cafe')
    cardapio.almoco = request.POST.get('almoco')
    cardapio.almoco_inicio = request.POST.get('hora-inicio-almoco')
    cardapio.almoco_inicio = request.POST.get('hora-final-almoco')
    cardapio.jantar = request.POST.get('cafe')
    cardapio.jantar_inicio = request.POST.get('hora-inicio-jantar')
    cardapio.jantar_inicio = request.POST.get('hora-final-jantar')
    cardapio.save()
    
    mostrar_cardapio = {
        "cardapio": Cardapio.objects.all()
    }
    
    return render(request, 'ETicketApp/pages/manager/menu.html', mostrar_cardapio)




