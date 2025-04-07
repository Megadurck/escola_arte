from django.apps import AppConfig


class InscricoesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inscricoes'
    
    def ready(self):
        # Importa os sinais para garantir que eles sejam registrados
        import inscricoes.signals
