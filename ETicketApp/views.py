from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from email.mime.image import MIMEImage
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
import traceback

from django.db.models import Q

from django.contrib.auth.decorators import user_passes_test, login_required 
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User, Group
from django.db import transaction 


from django import template
from .forms import *
from .models import *

import base64
import qrcode
from django.core.files.base import ContentFile

from django.urls import reverse

import requests
from django.contrib.auth.hashers import check_password, make_password
from datetime import datetime, date
from io import BytesIO

from decimal import Decimal
import random

from django.contrib.auth.decorators import permission_required

# Create your views here.
# ----------- usuario final ------------
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
        
        # metodo_pagamento = request.POST.get('metodo_pagamento')  # Adicione o método de pagamento no formulário
        
        # Gera um método de pagamento aleatório
        metodo_pagamento = random.choice([MetodoPagamentoEnum.PIX.value, MetodoPagamentoEnum.DINHEIRO.value, MetodoPagamentoEnum.CARTAO.value]) 
        
        if valor and metodo_pagamento:
            try:
                valor_decimal = Decimal(valor)
                
                # Verifica se o valor é positivo
                if valor_decimal <= 0:
                    messages.error(request, 'O valor deve ser positivo.')
                    return redirect('home')
                
                personal_data = get_object_or_404(DadoPessoal, usuario=request.user)
                
                # Busca a classificação com o maior peso (prioridade) do usuário
                classificacao_prioritaria = personal_data.classificacoes.order_by('prioridade').first()
                
                if classificacao_prioritaria:
                    limite_credito = classificacao_prioritaria.limite_credito
                    
                    # Verifica se a adição do valor ultrapassa o limite de crédito
                    if personal_data.credito + valor_decimal > limite_credito:
                        messages.error(request, f"O limite de crédito de R${limite_credito} será excedido.")
                        return redirect('home')
                
                # Adiciona o valor ao crédito do usuário
                personal_data.credito += valor_decimal
                personal_data.save()

                # Cria o registro de crédito
                Credito.objects.create(
                    usuario=request.user,
                    valor=valor_decimal,
                    metodo_pagamento=metodo_pagamento
                )
                
                messages.success(request, 'Crédito aumentado com sucesso!')
                return redirect('home')
            except (DadoPessoal.DoesNotExist, Decimal.InvalidOperation):
                messages.error(request, 'Falha ao aumentar crédito. Verifique o valor e tente novamente.')
                return redirect('home')
    return redirect('home')

@login_required
def pagamento(request):
    if request.method == "POST":
        valor = request.POST.get('valor')
        print(valor)
        context = {
            'valor': valor
        }
        return render(request,'ETicketApp/pages/user/pagamento.html', context)

@login_required
def menu(request):
    hoje = date.today()
    
    # Filtra o cardápio para cada tipo de refeição do dia
    cafe = Cardapio.objects.filter(data=hoje, tipo_refeicao="CAFE_DA_MANHA").first()
    almoco = Cardapio.objects.filter(data=hoje, tipo_refeicao="ALMOCO").first()
    jantar = Cardapio.objects.filter(data=hoje, tipo_refeicao="JANTAR").first()
    
    # Obtem o dado pessoal do usuário e a classificação com a maior prioridade
    dados_pessoais = DadoPessoal.objects.get(usuario=request.user)
    classificacao = dados_pessoais.classificacoes.order_by('prioridade').first()  # Assumindo prioridade ascendente

    # Prepara os valores com base na classificação
    valor_cafe = classificacao.valor_cafe_manha if classificacao else None
    valor_almoco = classificacao.valor_almoco if classificacao else None
    valor_jantar = classificacao.valor_jantar if classificacao else None

    # Adiciona os menus e os valores ao contexto
    context = {
        'cafe': cafe,
        'almoco': almoco,
        'jantar': jantar,
        'valor_cafe': valor_cafe,
        'valor_almoco': valor_almoco,
        'valor_jantar': valor_jantar,
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
        'foto': personal_data.foto,
    }
    
    return render(request, 'ETicketApp/pages/user/perfil.html', context)


def salvar_foto(foto_base64, usuario):
    # Decodifica a imagem
    format, imgstr = foto_base64.split(';base64,') 
    ext = format.split('/')[-1]  # Extrai a extensão do formato
    img_data = base64.b64decode(imgstr)  # Decodifica a imagem

    # Cria um arquivo temporário para a imagem
    file_name = f"{usuario.matricula}_foto.{ext}"  # Nome do arquivo
    file = ContentFile(img_data, name=file_name)

    # Salva a imagem no modelo
    usuario.foto.save(file_name, file)
    usuario.save()

# Defina a URL da API externa
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if not form.is_valid():
            return render(request, 'ETicketApp/pages/user/login.html', {'form': form})

        cpf = form.cleaned_data['cpf'].replace(".", "").replace("-", "")
        password = form.cleaned_data['password']

        if not cpf:
            messages.error(request, 'CPF é obrigatório.')
            return render(request, 'ETicketApp/pages/user/login.html', {'form': form})

        # personal_data = DadoPessoal.objects.filter(cpf=cpf).first()
        # if personal_data and password:
        #     if personal_data.usuario.check_password(password):
        #         auth_login(request, personal_data.usuario)
        #         return redirect('home')
        #     else:
        #         messages.error(request, 'Senha incorreta.')
        #         return render(request, 'ETicketApp/pages/user/login.html', {
        #             'form': form, 'error_message': 'Senha incorreta.'
        #         })

        # Se não encontrar localmente, consulta API externa
        headers = {'Authorization': f'Bearer {settings.BEARER_TOKEN}'}
        response = requests.post(settings.UFAC_API_URL, json={"cpf": cpf}, headers=headers)

        if response.status_code != 200:
            messages.error(request, 'Erro na API externa.')
            return render(request, 'ETicketApp/pages/user/login.html', {
                'form': form, 'error_message': 'Erro na API externa.'
            })

        api_data = response.json()
        user_data = None
        classifications = []
        max_weight = -1

        for data in api_data.get('response', []):
            if data.get('SITUACAO') == 'Ativo':
                classification_name = data.get('CLASSIFICACAO')
                classificacao, _ = Classificacao.objects.get_or_create(nome=classification_name)
                if classificacao.prioridade > max_weight:
                    user_data = data
                    max_weight = classificacao.prioridade
                    classifications = [classificacao]

        if not user_data:
            messages.error(request, 'Nenhum usuário ativo encontrado.')
            return render(request, 'ETicketApp/pages/user/login.html', {
                'form': form, 'error_message': 'Nenhum usuário ativo encontrado.'
            })

        # Extrai dados do usuário
        nome_completo = user_data.get('NOME')
        nome_social = user_data.get('NOME_SOCIAL')
        email = user_data.get('EMAIL')
        foto = user_data.get('FOTO')
        matricula = user_data.get('MATRICULA')
        unidade = user_data.get('UNIDADE')
        data_entrada = user_data.get('DT_ENTRADA')
        gratuito = user_data.get('GRATUIDADE') == 'S'

        # Atualiza ou cria usuário local
        usuario = None
        try:
            personal_data = DadoPessoal.objects.get(cpf=cpf)
            usuario = personal_data.usuario
            usuario.email = email
            usuario.save()

            personal_data.nome_completo = nome_completo
            personal_data.nome_social = nome_social
            personal_data.matricula = matricula
            personal_data.data_entrada = data_entrada
            personal_data.unidade = unidade
            personal_data.gratuito = gratuito
            personal_data.foto = foto
            personal_data.save()

        except DadoPessoal.DoesNotExist:
            usuario = User.objects.create(
                username=nome_completo,
                password=make_password(None),
                email=email,
            )
            personal_data = DadoPessoal.objects.create(
                usuario=usuario,
                nome_completo=nome_completo,
                nome_social=nome_social,
                cpf=cpf,
                matricula=matricula,
                data_entrada=data_entrada,
                unidade=unidade,
                credito=0.0,
                foto=foto,
                gratuito=gratuito,
            )

        # Define classificações (ManyToMany)
        personal_data.classificacoes.set(classifications)

        # Autentica o usuário
        auth_login(request, usuario)
        return redirect('home')

    # GET request
    form = LoginForm()
    return render(request, 'ETicketApp/pages/user/login.html', {'form': form})



@login_required
def historico(request):
    
    # Busca o histórico de créditos do usuário logado
    historico = Credito.objects.filter(usuario=request.user).order_by('-data', '-hora')
    
    context = {
        'historico': historico        # Passa o histórico para o template
    }
    
    return render(request, 'ETicketApp/pages/user/historico.html', context)

@login_required
def historico_refeicoes(request):

    historico_refeicoes = Refeicao.objects.filter(usuario=request.user).select_related('usuario', 'menu', 'ticket_unico').order_by('-data', '-hora')

    context = {
        'historico_refeicoes': historico_refeicoes,
    }
    
    return render(request, 'ETicketApp/pages/user/historico_refeicoes.html', context)

@login_required
def valorPaga(request):
    return render(request, 'ETicketApp/pages/user/valorPaga.html')

@login_required
def informacao(request):
    informacao = Informacao.objects.all().order_by('-data_publicacao')  # Ordena pela data de publicação, mais recente primeiro
    return render(request, 'ETicketApp/pages/user/informacao.html', {'informacao': informacao})

# ----------- usuario externo ------------

def valorPagaExterno (request):
    return render(request, 'ETicketApp/pages/user/valorPagaExterno.html')

def menuExterno (request):
    return render(request, 'ETicketApp/pages/user/menuExterno.html')



# ----------- usuario gerenciador ------------

def is_in_group(user, group_names):

    return user.groups.filter(name__in=group_names).exists()

def is_superuser(user):
    grupos = ['ADM', 'Colaborador', 'Bolsista']
    return user.is_superuser or is_in_group(user, grupos)

register = template.Library()

@register.filter
def in_groups(user, group_names):
    return user.groups.filter(name__in=group_names).exists()

@user_passes_test(is_superuser)
def dashboard (request):
    return render(request, 'ETicketApp/pages/manager/dashboard.html')

@user_passes_test(is_superuser)
def validar (request):
    return render(request, 'ETicketApp/pages/manager/validar.html')

@user_passes_test(is_superuser)
def mostrar_usuario(request):  
    if request.method == 'POST':
        codigo = request.POST.get('matricula')  # Pode ser matrícula (numérica) ou código do ticket (UUID)
        tipo_refeicao = ""
        valor = 0.00
        # Verifica se o código é numérico para tentar buscar DadoPessoal
        if codigo.isdigit():
            try:
                dados_pessoais = DadoPessoal.objects.get(matricula=codigo)
                # Obtém as classificações do usuário
                classificacoes = " / ".join(dados_pessoais.classificacoes.values_list('nome', flat=True))
            except DadoPessoal.DoesNotExist:
                dados_pessoais = None
        else:
            dados_pessoais = None
         
        current_hour = datetime.now().hour
        if current_hour < 10:
            tipo_refeicao = "CAFE_DA_MANHA"
        elif 10 <= current_hour < 17:
            tipo_refeicao = "ALMOCO"
        elif 17 <= current_hour:
            tipo_refeicao = "JANTAR"
           
        if dados_pessoais:    
            classificacao = dados_pessoais.classificacoes.order_by('prioridade').first()
            # Identifica o tipo de refeição com base no horário atual
            if tipo_refeicao == "CAFE_DA_MANHA":
                valor = classificacao.valor_cafe_manha
            elif tipo_refeicao == "ALMOCO":
                valor = classificacao.valor_almoco
            elif tipo_refeicao == "JANTAR":
                valor = classificacao.valor_jantar
                
            context = {
                'nome_completo': dados_pessoais.nome_completo,
                'cpf': dados_pessoais.cpf,
                'matricula': dados_pessoais.matricula,
                'credito': dados_pessoais.credito,
                'unidade': dados_pessoais.unidade,
                'classificacoes': classificacoes,
                'tipo_refeicao': tipo_refeicao,
                'valor': valor,
            }
            return render(request, 'ETicketApp/pages/manager/validarUsuario.html', context)

        if not dados_pessoais:
            
            try:
                print(f"Debug: Tentando buscar TicketUnico com código {codigo}")
                ticket = TicketUnico.objects.get(codigo=codigo)
                if ticket.valido:
                    # Verifica se o tipo de refeição do ticket corresponde ao horário atual
                    if ticket.tipo_refeicao == tipo_refeicao:
                        ticket.valido = False
                        ticket.save()
                        
                        # Registra a refeição
                        Refeicao.objects.create(
                            valor=ticket.valor,
                            gratuito=False,
                            data=datetime.now().date(),
                            hora=datetime.now().time(),
                            tipo_refeicao=tipo_refeicao,
                            menu=Cardapio.objects.filter(data=datetime.now().date(), tipo_refeicao=tipo_refeicao).first(),
                            ticket_unico=ticket
                        )
                        messages.success(request, 'Ticket validado com sucesso!')
                    else:
                        messages.error(request, 'Tipo de refeição inválido para o horário atual.')

                        return redirect('validar')
                else:
                    messages.error(request, 'Ticket já foi utilizado ou está inválido.')

                    return redirect('validar')
            except TicketUnico.DoesNotExist:
                messages.error(request, 'Código inválido. Não corresponde a uma matrícula ou ticket válido.')
                return redirect('validar')

    return render(request, 'ETicketApp/pages/manager/validarUsuario.html')

@user_passes_test(is_superuser)
def validar_usuario(request):
    if request.method == 'POST':
        matricula = request.POST.get('matricula')
        tipo_refeicao = request.POST.get('tipo_refeicao')

        try:
            # Busca o usuário pela matrícula
            dados_pessoais = DadoPessoal.objects.get(matricula=matricula)\
                
            if dados_pessoais and Refeicao.objects.filter(usuario=dados_pessoais.usuario, data=date.today(), tipo_refeicao=tipo_refeicao).exists():
                messages.error(request, f'{tipo_refeicao} já foi registrado para hoje.')
                print(f'Debug: {tipo_refeicao} já registrado para {dados_pessoais.usuario} na data {date.today()}')
                return redirect('validar')
            
            print(f'Debug: {tipo_refeicao} não registrado para {dados_pessoais.usuario} na data {date.today()}')
            refeicao = Refeicao.objects.filter(usuario=dados_pessoais.usuario, data=date.today(), tipo_refeicao=tipo_refeicao).first()
            print(refeicao)

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
                    tipo_refeicao=tipo_refeicao,
                    menu=Cardapio.objects.filter(data=datetime.now().date(), tipo_refeicao=tipo_refeicao).first(),
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
                    tipo_refeicao=tipo_refeicao,
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
def cardapio(request):
    # Recupera todos os cardápios ordenados pela data, do mais recente ao mais antigo
    cardapios = Cardapio.objects.all().order_by('-data')
    
    context = {
        'cardapios': cardapios,
    }
    
    return render(request, 'ETicketApp/pages/manager/cardapio.html', context)

@user_passes_test(is_superuser)
def adicionar_cardapio(request):
    if request.method == 'POST':
        form = CardapioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cardapio')
    else:
        form = CardapioForm()
    return render(request, 'ETicketApp/pages/manager/cardapio_form.html', {'form': form})

@user_passes_test(is_superuser)
def editar_cardapio(request, id):
    cardapio = get_object_or_404(Cardapio, id=id)
    if request.method == 'POST':
        form = CardapioForm(request.POST, instance=cardapio)
        if form.is_valid():
            form.save()
            return redirect('cardapio')
    else:
        form = CardapioForm(instance=cardapio)
    return render(request, 'ETicketApp/pages/manager/cardapio_form.html', {'form': form})

@user_passes_test(is_superuser)
def excluir_cardapio(request, id):
    cardapio = get_object_or_404(Cardapio, id=id)
    cardapio.delete()
    return redirect('cardapio')

@user_passes_test(is_superuser)
def vender (request):
    return render(request, 'ETicketApp/pages/manager/vender.html')

@user_passes_test(is_superuser)
def vendaUnico (request):
    return render(request, 'ETicketApp/pages/manager/vendaUnico.html')

@user_passes_test(is_superuser)
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
            return render(request, 'ETicketApp/pages/manager/usuarioCompra.html', context)
        if request.POST.get('valor'):
            valor = request.POST.get('valor')
            # metodo_pagamento = request.POST.get('metodo_pagamento')  # Adicione o método de pagamento no formulário
        
            # Gera um método de pagamento aleatório
            metodo_pagamento = random.choice([MetodoPagamentoEnum.PIX.value, MetodoPagamentoEnum.DINHEIRO.value, MetodoPagamentoEnum.CARTAO.value]) 
            if valor:         
                try:
                    valor_decimal = Decimal(valor)
                    
                    if valor_decimal <= 0:
                        messages.error(request, 'O valor deve ser positivo.')  # Mensagem de erro se o valor for negativo ou zero
                        return redirect('vender')
                    
                    personal_data = get_object_or_404(DadoPessoal, usuario=request.user)
                    
                                    # Busca a classificação com o maior peso (prioridade) do usuário
                    classificacao_prioritaria = personal_data.classificacoes.order_by('prioridade').first()
                    
                    if classificacao_prioritaria:
                        limite_credito = classificacao_prioritaria.limite_credito
                        
                        if personal_data.credito + valor_decimal > limite_credito:
                            messages.error(request, f"O limite de crédito de R${limite_credito} será excedido.")
                            return redirect('vender')
                    
                    personal_data.credito += valor_decimal
                    personal_data.save()
                    
                
                    Credito.objects.create(
                        usuario=request.user,
                        valor=valor_decimal,
                        metodo_pagamento=metodo_pagamento
                    )
                    messages.success(request, 'Crédito aumentado com sucesso!') 
                    return redirect('vender')  
                except (DadoPessoal.DoesNotExist, Decimal.InvalidOperation):
                    messages.error(request, 'Falha ao aumentar crédito. Verifique o valor e tente novamente.')  
                    return redirect('vender') 
            
    return render(request, 'ETicketApp/pages/manager/usuarioCompra.html')

@user_passes_test(is_superuser)
def listar_usuarios_view(request):
    base_query_set = User.objects.select_related('dadopessoal').prefetch_related('groups')

    search_query = request.GET.get('q', None)
    tipo_usuario_filter_id_str = request.GET.get('tipo_usuario', None)

    todos_os_grupos_para_filtro = Group.objects.all().order_by('name')

    if search_query:
        users_after_text_search = base_query_set.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(dadopessoal__nome_completo__icontains=search_query) | 
            Q(dadopessoal__cpf__icontains=search_query)             
        ).distinct()
    else:
        users_after_text_search = base_query_set.all()


    final_users_list = users_after_text_search 

    if tipo_usuario_filter_id_str: 
        try:
            group_id_para_filtrar = int(tipo_usuario_filter_id_str)
            final_users_list = users_after_text_search.filter(groups__id=group_id_para_filtrar)
        except ValueError:
            final_users_list = users_after_text_search.none() 
    else: 

        final_users_list = users_after_text_search.filter(groups__isnull=False).distinct()

    final_users_list = final_users_list.order_by('username')

    context = {
        'usuarios': final_users_list,
        'todos_os_grupos_para_filtro': todos_os_grupos_para_filtro,
    }
    return render(request, 'ETicketApp/pages/manager/usuarios.html', context)

@user_passes_test(is_superuser)
def add_papel_usuario (request):
    return render(request, 'ETicketApp/pages/manager/add_user.html')

@user_passes_test(is_superuser)
def buscar_selecionar_usuario(request):
    
    search_term = request.GET.get('search_query', '')
    users_found_with_dados = None 

    if search_term:
        users_found_with_dados = DadoPessoal.objects.filter(
            Q(nome_completo__icontains=search_term) |
            Q(cpf__icontains=search_term) |         
            Q(unidade__icontains=search_term) |
            Q(usuario__username__icontains=search_term)
        ).select_related('usuario').distinct()
        
        if not users_found_with_dados:
            messages.info(request, 'Nenhum usuário encontrado com os critérios fornecidos.')
            
    print(f"Debug: search_term={search_term}, users_found_with_dados={users_found_with_dados}")

    context = {
        'users_found_with_dados': users_found_with_dados,
        'search_term': search_term,
        'page_title': 'Buscar e Gerenciar Usuários'
    }
    # This template will display the search form and results
    return render(request, 'ETicketApp/pages/manager/buscar_selecionar_usuario.html', context)

ADM_GROUP_NAME = "ADM"

@user_passes_test(is_superuser)
def editar_papel_usuario(request, usuario_id): # Renomeado de 'id' para 'usuario_id' para clareza
    usuario_alvo = get_object_or_404(User, id=usuario_id)
    dadopessoal_alvo = getattr(usuario_alvo, 'dadopessoal', None) # Assumindo relação OneToOne 'dadopessoal'

    try:
        adm_group_obj = Group.objects.get(name=ADM_GROUP_NAME)
    except Group.DoesNotExist:
        messages.error(request, f"Erro crítico: O grupo de administradores '{ADM_GROUP_NAME}' não existe.")
        return redirect('buscar_selecionar_usuario') # Ou uma página de erro apropriada

    # Verifica se o usuário logado (request.user) é ADM
    request_user_is_adm = request.user.groups.filter(name=ADM_GROUP_NAME).exists() or request.user.is_superuser

    if request.method == 'POST':
        novo_papel_id_str = request.POST.get('papel')
        
        # Usuário alvo era ADM antes desta alteração?
        alvo_era_adm = usuario_alvo.groups.filter(id=adm_group_obj.id).exists()

        # 1. Tentativa de atribuir o papel ADM
        if novo_papel_id_str and int(novo_papel_id_str) == adm_group_obj.id:
            if not request_user_is_adm:
                messages.error(request, "Apenas administradores podem atribuir o papel de Administrador.")
                # Re-renderiza o formulário sem alterar, idealmente com os dados e erros
                # Para simplificar, redirecionando, mas é melhor re-renderizar o form:
                return redirect('editar_papel_usuario', usuario_id=usuario_alvo.id)
        
        # 2. Tentativa de remover/alterar o papel de um ADM existente por um não-ADM
        if alvo_era_adm and not request_user_is_adm:
            # Se o alvo era ADM e o usuário logado não é ADM,
            # a única operação permitida é manter o alvo como ADM.
            # Se novo_papel_id_str for vazio (remover papel) ou diferente do ID do ADM, é uma tentativa inválida.
            if not novo_papel_id_str or (novo_papel_id_str and int(novo_papel_id_str) != adm_group_obj.id):
                messages.error(request, "Você não tem permissão para alterar o papel de um Administrador.")
                return redirect('editar_papel_usuario', usuario_id=usuario_alvo.id)

        # Processar a mudança de grupo
        usuario_alvo.groups.clear() # Remove de todos os grupos atuais (assumindo um papel por vez)
        if novo_papel_id_str:
            try:
                novo_papel = Group.objects.get(id=int(novo_papel_id_str))
                usuario_alvo.groups.add(novo_papel)
            except (ValueError, Group.DoesNotExist):
                messages.error(request, "Papel selecionado é inválido.")
                # Melhor re-renderizar o formulário com o erro.
                return redirect('editar_papel_usuario', usuario_id=usuario_alvo.id)
        
        messages.success(request, f"Papel de {usuario_alvo.username} atualizado com sucesso.")
        search_query = request.GET.get('search_query') # Mantém o filtro de busca ao voltar
        redirect_url = reverse('buscar_selecionar_usuario')
        if search_query:
            return redirect(f"{redirect_url}?search_query={search_query}")
        return redirect(redirect_url)

    # Lógica para GET (exibir o formulário)
    todos_os_papeis = Group.objects.all()
    current_group_of_target = usuario_alvo.groups.first()
    current_group_id_of_target = current_group_of_target.id if current_group_of_target else None

    # O usuário alvo é atualmente um ADM?
    target_user_is_currently_adm = (current_group_id_of_target == adm_group_obj.id)

    # Desabilitar todo o formulário de mudança de papel?
    # Sim, se o alvo é ADM e o usuário logado não é ADM.
    disable_entire_form = (target_user_is_currently_adm and not request_user_is_adm)

    papeis_options_for_template = []
    for papel in todos_os_papeis:
        option_is_adm_role = (papel.id == adm_group_obj.id)
        # Por padrão, uma opção não está desabilitada individualmente no <option>
        # A desabilitação geral do <select> é controlada por 'disable_entire_form'
        option_disabled_individually = False

        if not disable_entire_form: # Se o formulário não estiver totalmente desabilitado
            if option_is_adm_role and not request_user_is_adm:
                # Usuário logado não é ADM, e esta é a opção ADM.
                # Desabilita a opção ADM se o alvo não for já ADM.
                if not target_user_is_currently_adm:
                    option_disabled_individually = True
        
        papeis_options_for_template.append({
            'value': str(papel.id), # Valor para o <option value="">
            'name': papel.name,
            'is_disabled_individually': option_disabled_individually
        })

    context = {
        'usuario': usuario_alvo,
        'dadopessoal': dadopessoal_alvo,
        'papeis_options': papeis_options_for_template,
        'current_group_value': str(current_group_id_of_target) if current_group_id_of_target else "",
        'disable_form_controls': disable_entire_form, # Para desabilitar <select> e botão Salvar
    }
    return render(request, 'ETicketApp/pages/manager/definir_papel_usuario.html', context)

@user_passes_test(is_superuser)
def excluir_papel_usuario(request, id):
    usuario = get_object_or_404(User, id=id)  # Busca o usuário pelo ID
    
    # Remove o usuário de todos os grupos
    usuario.groups.clear()
    
    messages.success(request, 'Usuário removido de todos os grupos!')
    return redirect('usuarios')  # Redireciona para a lista de usuários



@user_passes_test(is_superuser)
def cadastrar_cardapio(request):
    if request.method == 'POST':
        # Obtém os dados do formulário
        data = request.POST.get('data')
        cafe = request.POST.get('cafe')
        almoco = request.POST.get('almoco')
        jantar = request.POST.get('jantar')

        # Valida se todos os campos estão preenchidos
        if data and cafe and almoco and jantar:
            try:
                # Converte a data para o formato correto
                data_formatada = datetime.strptime(data, '%Y-%m-%d')

                # Cria um novo cardápio e salva no banco de dados
                novo_cardapio = Cardapio(
                    data=data_formatada,
                    cafe=cafe,
                    almoco=almoco,
                    jantar=jantar
                )
                novo_cardapio.save()

                # Mensagem de sucesso
                messages.success(request, 'Cardápio cadastrado com sucesso!')
                return redirect('cardapio')  # Redireciona para a página de cardápio

            except Exception as e:
                # Em caso de erro, mostra uma mensagem de erro
                messages.error(request, f'Erro ao cadastrar o cardápio: {str(e)}')
                return redirect('cardapio')  # Redireciona para a mesma página para tentar novamente

        else:
            # Se algum campo estiver vazio, mostra uma mensagem de erro
            messages.error(request, 'Por favor, preencha todos os campos.')
            return redirect('cardapio')
        


    # Caso contrário, exibe o formulário de cadastro de cardápio
    return render(request, 'ETicketApp/pages/manager/cardapio.html')

@user_passes_test(is_superuser)
def classificacao(request):
    classificacoes = Classificacao.objects.all()
    return render(request, 'ETicketApp/pages/manager/classificacao.html', {'classificacoes': classificacoes})

@user_passes_test(is_superuser)
def classificacao_add_edit(request, pk=None):
    if pk:
        classificacao = get_object_or_404(Classificacao, pk=pk)
    else:
        classificacao = None

    if request.method == "POST":
        form = ClassificacaoForm(request.POST, instance=classificacao)
        if form.is_valid():
            form.save()
            return redirect('classificacao')
    else:
        form = ClassificacaoForm(instance=classificacao)

    return render(request, 'ETicketApp/pages/manager/classificacao_form.html', {'form': form})

@user_passes_test(is_superuser)
def classificacao_delete(request, pk):
    classificacao = get_object_or_404(Classificacao, pk=pk)
    if request.method == "POST":
        classificacao.delete()
        return redirect('classificacao')
    return render(request, 'ETicketApp/pages/manager/classificacao.html', {'classificacao': classificacao})

def enviar_email_com_ticket(destinatario_email, lista_tickets_criados):
    """
    Envia um único e-mail com os detalhes de todos os tickets comprados.
    """
    if not lista_tickets_criados:
        print("Nenhum ticket para enviar por e-mail.")
        return False

    assunto = f"Seus Tickets RU ({len(lista_tickets_criados)} unidades)"
    
    tickets_para_template = []
    anexos_email = []

    for i, ticket_obj in enumerate(lista_tickets_criados):
        qr_data = ticket_obj.codigo
        qr_img = qrcode.make(qr_data)
        
        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        qr_image_data = buffer.getvalue()

        qr_code_cid_unico = f'qrcode_ticket_{ticket_obj.codigo}_{i}' 

        qr_image_mime = MIMEImage(qr_image_data)
        qr_image_mime.add_header('Content-ID', f'<{qr_code_cid_unico}>')
        qr_image_mime.add_header('Content-Disposition', 'inline', filename=f'qrcode_{ticket_obj.codigo}.png')
        anexos_email.append(qr_image_mime)

        tickets_para_template.append({
            'codigo': ticket_obj.codigo,
            'valor': ticket_obj.valor,
            'tipo_refeicao': ticket_obj.get_tipo_refeicao_display(),
            'qr_code_cid': qr_code_cid_unico, 
        })

    contexto_email = {
        'lista_tickets': tickets_para_template,
        'quantidade_total': len(lista_tickets_criados),
    }
    
    html_corpo = render_to_string('ETicketApp/emails/email_ticket_unico.html', contexto_email)
    
    email = EmailMessage(
        assunto,
        html_corpo,
        settings.DEFAULT_FROM_EMAIL,
        [destinatario_email]
    )
    email.content_subtype = "html"
    
    for anexo in anexos_email:
        email.attach(anexo)

    try:
        email.send()
        return True
    except Exception as e:
        print(f"Erro detalhado ao enviar e-mail de resumo para {destinatario_email}:")
        print(f"Exceção: {type(e).__name__} - {e}")
        print(traceback.format_exc())
        return False


def gerar_ticket_unico(request):
    if request.method == 'POST':
        email_usuario = request.POST.get('email')
        classificacao_nome = request.POST.get('classificacao')
        pagamento = request.POST.get('pagamento')
        qtd_cafe = int(request.POST.get('cafe', 0))
        qtd_almoco = int(request.POST.get('almoco', 0))
        qtd_janta = int(request.POST.get('janta', 0))

        if not email_usuario:
            messages.error(request, 'O campo e-mail é obrigatório.')
            return render(request, 'ETicketApp/pages/manager/vendaUnico.html', {'form_data': request.POST})

        try:
            classificacao_obj = Classificacao.objects.get(nome=classificacao_nome)
            # Lista para armazenar os objetos TicketUnico criados
            lista_tickets_criados_nesta_transacao = [] 

            with transaction.atomic():
                for _ in range(qtd_cafe):
                    ticket = TicketUnico.objects.create(
                        valor=classificacao_obj.valor_cafe_manha,
                        metodo_pagamento=pagamento,
                        tipo_refeicao='CAFE_DA_MANHA', # Use os valores exatos das suas choices
                        classificacao=classificacao_obj
                    )
                    lista_tickets_criados_nesta_transacao.append(ticket)
                
                for _ in range(qtd_almoco):
                    ticket = TicketUnico.objects.create(
                        valor=classificacao_obj.valor_almoco,
                        metodo_pagamento=pagamento,
                        tipo_refeicao='ALMOCO', # Use os valores exatos das suas choices
                        classificacao=classificacao_obj
                    )
                    lista_tickets_criados_nesta_transacao.append(ticket)

                for _ in range(qtd_janta):
                    ticket = TicketUnico.objects.create(
                        valor=classificacao_obj.valor_jantar,
                        metodo_pagamento=pagamento,
                        tipo_refeicao='JANTAR', # Use os valores exatos das suas choices (corrigido de tipo_re_refeicao)
                        classificacao=classificacao_obj
                    )
                    lista_tickets_criados_nesta_transacao.append(ticket)
            
            # Após criar todos os tickets da transação:
            if lista_tickets_criados_nesta_transacao:
                # Envia um único e-mail com todos os tickets
                email_foi_enviado = enviar_email_com_ticket(email_usuario, lista_tickets_criados_nesta_transacao)
                
                quantidade_criada = len(lista_tickets_criados_nesta_transacao)
                if email_foi_enviado:
                    messages.success(request, f'{quantidade_criada} Tickets gerados com sucesso! Um e-mail de confirmação com todos os tickets foi enviado.')
                else:
                    messages.warning(request, f'{quantidade_criada} Tickets foram gerados, mas houve uma falha ao enviar o e-mail de confirmação. Por favor, verifique os tickets na sua área de listagem ou contate o suporte.')
                
                # Armazena os IDs dos tickets criados na sessão (como antes)
                request.session['tickets_criados_ids'] = [t.id for t in lista_tickets_criados_nesta_transacao]
            else:
                messages.info(request, 'Nenhuma quantidade de ticket foi especificada.')
            
            return redirect('listar_tickets')

        except Classificacao.DoesNotExist:
            messages.error(request, 'Classificação não encontrada.')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro inesperado ao gerar os tickets: {e}')
            # import traceback # Para debug no console do servidor
            # print(traceback.format_exc())
            
    return render(request, 'ETicketApp/pages/manager/vendaUnico.html')

def listar_tickets(request):
    # Recupera os IDs dos tickets criados armazenados na sessão
    tickets_ids = request.session.get('tickets_criados_ids', [])
    tickets_criados = TicketUnico.objects.filter(id__in=tickets_ids)

    # Limpa os IDs da sessão após exibir os tickets
    request.session['tickets_criados_ids'] = []

    return render(request, 'ETicketApp/pages/manager/mostra_ticket_unico.html', {'tickets': tickets_criados})

def gerar_qrcode(request, ticket_id):
    ticket = TicketUnico.objects.get(id=ticket_id)
    # Gera o QR code com o valor de `codigo` do ticket
    qr = qrcode.make(str(ticket.codigo))
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer, content_type="image/png")

def informacao_manage(request):
    informacao = Informacao.objects.all()
    return render(request, 'ETicketApp/pages/manager/informacao.html', {'informacao': informacao})

def adicionar_informacao(request):
    if request.method == 'POST':
        form = InformacaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "informação adicionado com sucesso!")
            return redirect('informacao_manage')
    else:
        form = InformacaoForm()
    return render(request, 'ETicketApp/pages/manager/informacao_form.html', {'form': form})

def editar_informacao(request, id):
    informacao = get_object_or_404(Informacao, id=id)
    if request.method == 'POST':
        form = InformacaoForm(request.POST, instance=informacao)
        if form.is_valid():
            form.save()
            messages.success(request, "informação atualizado com sucesso!")
            return redirect('informacao_manage')
    else:
        form = InformacaoForm(instance=informacao)
    return render(request, 'ETicketApp/pages/manager/informacao_form.html', {'form': form, 'informacao': informacao})

def deletar_informacao(request, id):
    informacao = get_object_or_404(Informacao, id=id)
    if request.method == 'POST':
        informacao.delete()
        messages.success(request, "informacao deletado com sucesso!")
        return redirect('informacao_manage')
    
def _preprocessar_permissoes_para_template(form_group):
    """
    Prepara as permissões do formulário para serem agrupadas corretamente no template.
    """
    permissions_para_template = []
    if 'permissions' in form_group.fields and hasattr(form_group['permissions'], '__iter__'):
        for bound_widget_choice in form_group['permissions']:
            choice_label_original = bound_widget_choice.choice_label
            chave_de_agrupamento = ""
            partes = str(choice_label_original).split(' | ')

            if len(partes) == 3:  # Formato: "app_label | model_name | permission_name"
                chave_de_agrupamento = partes[1].strip()  # Pega "model_name"
            elif len(partes) == 1: # Formato: "Can add User Profile"
                label_apenas = partes[0].strip()
                prefixos_acao = ["Can add ", "Can change ", "Can delete ", "Can view "]
                nome_objeto = label_apenas
                # Tenta remover prefixos (case-insensitive)
                for prefixo in prefixos_acao:
                    if nome_objeto.lower().startswith(prefixo.lower()):
                        nome_objeto = nome_objeto[len(prefixo):]
                        break
                chave_de_agrupamento = nome_objeto.strip()
            else: # Fallback
                chave_de_agrupamento = partes[0].strip() if partes else choice_label_original
            
            permissions_para_template.append({
                'widget': bound_widget_choice,
                'label_original': choice_label_original,
                'chave_agrupamento': chave_de_agrupamento.lower(), # Usar minúsculas para agrupar, |title no template
            })
    return permissions_para_template



def permissoes(request):
    groups = Group.objects.all()
    context = {
        'groups': groups,
    }
    return render(request, 'ETicketApp/pages/manager/permissoes.html', context)

def adicionar_permissoes(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grupo de Permissões Cadastrado com Sucesso!')
            return redirect('permissoes') 
        else:

            messages.error(request, 'Não Foi Possível Cadastrar o Grupo de Permissões. Verifique os erros abaixo.')
            permissions_processadas = _preprocessar_permissoes_para_template(form)
    else:
        form = GroupForm()
        permissions_processadas = _preprocessar_permissoes_para_template(form)

    context = {
        'form': form,
        'permissions_processadas': permissions_processadas, 
    }
    return render(request, 'ETicketApp/pages/manager/permissoes_form.html', context)

def editar_permissoes(request, id):
    grupo = get_object_or_404(Group, id=id)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=grupo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grupo de Permissões Atualizado com Sucesso!')
            return redirect('permissoes')
        else:
            # print(form.errors) # Para debug
            messages.error(request, "Não foi possível Editar esse Grupo. Verifique os erros abaixo.")
            # Se o formulário for inválido, precisamos reprocessar as permissões para exibição
            permissions_processadas = _preprocessar_permissoes_para_template(form)
    else:
        form = GroupForm(instance=grupo)
        permissions_processadas = _preprocessar_permissoes_para_template(form)
        
    context = {
        'form': form,
        'grupo': grupo, # Pode ser útil ter o objeto grupo no contexto também
        'permissions_processadas': permissions_processadas, # Adicionado ao contexto
    }
    return render(request, 'ETicketApp/pages/manager/permissoes_form.html', context)

def deletar_permissoes(request, id):
    grupo_para_deletar = get_object_or_404(Group, id=id)
    grupo_para_deletar.delete()
    messages.success(request, 'Grupo Deletado com Sucesso!')
    return redirect('permissoes')