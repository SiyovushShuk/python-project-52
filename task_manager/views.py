from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


class LogoutView(View):
    def post(self, request):
        from django.contrib.auth import logout
        logout(request)
        messages.success(request, 'Вы разлогинены')
        return redirect('home')

    def get(self, request):
        return redirect('home')
