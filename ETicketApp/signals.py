from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.apps import AppConfig, apps
from django.contrib.contenttypes.models import ContentType

def add_permissions(sender, **kwargs):
    
    def grant_all_permissions_to_manager():
        gerente_group, _ = Group.objects.get_or_create(name="ADM")
        all_permissions = Permission.objects.all()
        gerente_group.permissions.set(all_permissions)
        gerente_group.save()

    grant_all_permissions_to_manager()
    
    grupos_permissoes = {
        "Bolsista": [
            ("auth", "user", ["view"]),
            ("eticketapp", "dadopessoal", ["view"]),
            ("eticketapp", "refeicao", ["add"]),
            ("eticketapp", "cardapio", ["add", "change", "delete", "view"]),
            ("eticketapp", "credito", ["view","change"]), 
            ("eticketapp", "classificação", ["view"]), 
        ],
        "Colaborador": [
            ("auth", "user", ["view"]),
            ("eticketapp", "dadopessoal", ["view"]),
            ("eticketapp", "refeicao", ["add"]),
            ("eticketapp", "cardapio", ["add", "change", "delete", "view"]),
            ("eticketapp", "credito", ["view","change"]), 
            ("eticketapp", "classificação", ["add", "change", "delete", "view"]), 
            ("eticketapp", "ticketunico", ["add"]), 
        ],
    }

    for grupo_nome, permissoes in grupos_permissoes.items():
        grupo, created = Group.objects.get_or_create(name=grupo_nome)
        for app_label, model, actions in permissoes:
            try:
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                for action in actions:
                    codename = f"{action}_{model}"
                    permission = Permission.objects.filter(codename=codename, content_type=content_type).first()
                    if permission:
                        grupo.permissions.add(permission)
                        print(f"✅ Permissão '{codename}' adicionada ao grupo '{grupo_nome}'.")
                    else:
                        print(f"⚠️ Permissão '{codename}' não encontrada para '{app_label}.{model}'.")
            except ContentType.DoesNotExist:
                print(f"⚠️ ContentType não encontrado: '{app_label}.{model}'")
                
post_migrate.connect(add_permissions)