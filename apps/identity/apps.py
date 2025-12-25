from django.apps import AppConfig

class IdentityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.identity' # <-- Must match the folder structure
    label = 'identity'     # <-- Force the label to be 'identity' to match AUTH_USER_MODEL