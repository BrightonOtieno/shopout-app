from django.apps import AppConfig


class BaseConfig(AppConfig):
    name = 'base'

    # for signals

    def ready(self):
        import base.signals
