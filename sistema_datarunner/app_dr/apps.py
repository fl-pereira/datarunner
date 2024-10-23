from django.apps import AppConfig

class AppDrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_dr'

    def ready(self):
        import app_dr.signals
