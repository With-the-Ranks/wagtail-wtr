from django.apps import AppConfig


class WtrxConfig(AppConfig):
    name = "wagtail_wtr.wtrx"
    label = "wagtail_wtr_wtrx"
    verbose_name = "With the Ranks Extensions"

    def ready(self):
        pass
