from django.apps import AppConfig


class DataPipelineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.data_pipeline'
    verbose_name = 'Data Pipeline'
