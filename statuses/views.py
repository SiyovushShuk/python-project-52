from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import StatusForm
from .models import Status


class StatusesListView(LoginRequiredMixin, ListView):
    model = Status
    template_name = 'statuses/statuses_list.html'
    context_object_name = 'statuses'
    ordering = ['id']
    login_url = reverse_lazy('login')
    redirect_field_name = None


class StatusCreateView(LoginRequiredMixin, CreateView):
    model = Status
    form_class = StatusForm
    template_name = 'statuses/create.html'
    success_url = reverse_lazy('statuses_list')
    login_url = reverse_lazy('login')
    redirect_field_name = None

    def form_valid(self, form: StatusForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, 'Статус успешно создан')
        return response


class StatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Status
    form_class = StatusForm
    template_name = 'statuses/update.html'
    success_url = reverse_lazy('statuses_list')
    login_url = reverse_lazy('login')
    redirect_field_name = None

    def form_valid(self, form: StatusForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, 'Статус успешно изменен')
        return response


class StatusDeleteView(LoginRequiredMixin, DeleteView):
    model = Status
    template_name = 'statuses/delete.html'
    success_url = reverse_lazy('statuses_list')
    login_url = reverse_lazy('login')
    redirect_field_name = None

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        try:
            response = super().post(request, *args, **kwargs)
            messages.success(request, 'Статус успешно удален')
            return response
        except IntegrityError:
            messages.error(request, 'Невозможно удалить статус, потому что он используется')
            return redirect('statuses_list')
