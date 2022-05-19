from django.apps import AppConfig

from eventual.manager import install_eventual


class EventualConfig(AppConfig):
    name = "eventual"

    def ready(self):
        install_eventual()
