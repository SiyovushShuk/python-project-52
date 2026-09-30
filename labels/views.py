from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import LabelForm
from .models import Label


class LabelsListView(LoginRequiredMixin, ListView):
    model = Label
    template_name = 'labels/labels_list.html'
    context_object_name = 'labels'
    ordering = ['id']
    login_url = reverse_lazy('login')
    redirect_field_name = None


class LabelCreateView(LoginRequiredMixin, CreateView):
    model = Label
    form_class = LabelForm
    template_name = 'labels/create.html'
    success_url = reverse_lazy('labels_list')
    login_url = reverse_lazy('login')
    redirect_field_name = None

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Метка успешно создана')
        return response


class LabelUpdateView(LoginRequiredMixin, UpdateView):
    model = Label
    form_class = LabelForm
    template_name = 'labels/update.html'
    success_url = reverse_lazy('labels_list')
    login_url = reverse_lazy('login')
    redirect_field_name = None

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Метка успешно изменена')
        return response


class LabelDeleteView(LoginRequiredMixin, DeleteView):
    model = Label
    template_name = 'labels/delete.html'
    success_url = reverse_lazy('labels_list')
    login_url = reverse_lazy('login')
    redirect_field_name = None

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.tasks.exists():
            messages.error(request, 'Невозможно удалить метку, потому что она используется')
            return redirect('labels_list')
        try:
            response = super().post(request, *args, **kwargs)
            messages.success(request, 'Метка успешно удалена')
            return response
        except IntegrityError:
            messages.error(request, 'Невозможно удалить метку, потому что она используется')
            return redirect('labels_list')
