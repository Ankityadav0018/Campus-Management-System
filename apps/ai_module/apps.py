from django.apps import AppConfig

class AiModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_module'
    label = 'ai_module'
    verbose_name = 'AI Module (Face Recognition, Rush Prediction, Absentee Alert)'
