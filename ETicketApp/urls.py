from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import *

urlpatterns = [
    path('', home, name='home'), 
    path('aumentar-credito/', aumentar_credito, name='aumentar-credito'),
    path('pagamento/', pagamento, name='pagamento'),
    path('menu/', menu, name='menu'),
    path('perfil/', perfil, name='perfil'),
    path('login/', login, name='login'),
    path('historico/', historico, name='historico'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),    
    
    path('manage/', dashboard, name='manage'), # home
    path('manage/validar/', validar, name='validar'),
    path('manage/validarUsuario/', validarUsuario, name='validarUsuario'),
    path('manage/validar_usuario/', validar_usuario, name='validar_usuario'),
    path('manage/ticketUnico/', ticketUnico, name='ticketUnico'),
    path('manage/relatorio/', relatorio, name='relatorio'),
    path('manage/cardapio/', cardapio, name='cardapio'),
    path('manage/ticketUnico/', ticketUnico, name='ticketUnico'),
    path('manage/vender/', vender, name='vender'),    
    path('manage/vendaUnico/', vendaUnico, name='vendaUnico'),  
    path('manage/usuarioCompra/', usuarioCompra, name='usuarioCompra'),
    path('manage/usuarios/', usuarios, name='usuarios'),
    path('manage/add_usuario/', add_usuario, name='adicionarUsuario') ,
    path('manage/cardapioExterno', cardapioExterno, name='cardapioExterno')
    
]