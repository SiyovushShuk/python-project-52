from __future__ import annotations

from django.apps import AppConfig


class LabelsConfig(AppConfig):
    name = 'labels'

    def ready(self) -> None:
        pass
