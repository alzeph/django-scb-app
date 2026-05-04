
from django.apps import AppConfig


class ScbAuthAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scb_auth"
    verbose_name = "SCB Auth"

    def ready(self) -> None:
        from scb_auth import signals
        from scb_auth.conf import scb_config
        scb_config.validate()
        
        