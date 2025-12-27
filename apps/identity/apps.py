from django.apps import AppConfig

class IdentityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.identity'
    # REMOVE the 'label = identity' line. 
    # Django automatically detects the label 'identity' from the name 'apps.identity'.