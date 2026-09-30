from __future__ import annotations

from django.apps import AppConfig


class StatusesConfig(AppConfig):
    name = 'statuses'

    def ready(self) -> None:
        pass
