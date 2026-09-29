from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
)
from django_filters.views import FilterView

from .filters import TaskFilter
from .forms import TaskForm
from .models import Task


class TasksListView(LoginRequiredMixin, FilterView):
    model = Task
    template_name = 'tasks/tasks_list.html'
    context_object_name = 'tasks'
    ordering = ['id']
    login_url = reverse_lazy('login')
    redirect_field_name = None
    filterset_class = TaskFilter

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related('status', 'author', 'executor')
            .prefetch_related('labels')
        )


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/detail.html'
    context_object_name = 'task'
    login_url = reverse_lazy('login')
    redirect_field_name = None

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related('status', 'author', 'executor')
            .prefetch_related('labels')
        )


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/create.html'
    success_url = reverse_lazy('tasks_list')
    login_url = reverse_lazy('login')
    redirect_field_name = None

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Задача успешно создана')
        return response


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/update.html'
    success_url = reverse_lazy('tasks_list')
    login_url = reverse_lazy('login')
    redirect_field_name = None

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Задача успешно изменена')
        return response


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/delete.html'
    success_url = reverse_lazy('tasks_list')
    login_url = reverse_lazy('login')
    redirect_field_name = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        task = self.get_object()
        if task.author_id != request.user.pk:
            messages.error(request, 'Задачу может удалить только её автор')
            return redirect('tasks_list')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author_id != request.user.pk:
            messages.error(request, 'Задачу может удалить только её автор')
            return redirect('tasks_list')
        messages.success(request, 'Задача успешно удалена')
        return super().post(request, *args, **kwargs)
