from django.apps import AppConfig

class HrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hr'   # Point to the folder
    label = 'hr'       # This is the "Nickname" the command looks for