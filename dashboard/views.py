from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

from account.decorators import employee_required
from account.models import *
from dashboard.forms import *

# Create your views here.

User = get_user_model()

def admin_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user_number = form.cleaned_data['user_number']
            password = form.cleaned_data['password']
            user = authenticate(user_number=user_number, password=password)
            if user is not None:
                user.is_active = True
                user.save()
                login(request, user)
                return redirect('admin_index')
    else:
        form = LoginForm()
    return render(request, 'dashboard/login.html', {'form': form})


def admin_logout(request):
    if request.user.is_authenticated:
        request.user.is_active = False
        request.user.save()
    logout(request)
    return redirect('login')


@employee_required
def admin_index_view(request):
    return render(request, 'dashboard/index.html')
