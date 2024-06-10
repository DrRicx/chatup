from django.contrib.auth import login, logout
from django.contrib.contenttypes.models import ContentType
from django.forms import modelform_factory
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from account.decorators import employee_required
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
    allowed_app_labels = ['chat']

    # Retrieve content types, including only the specified app labels
    content_types = ContentType.objects.filter(app_label__in=allowed_app_labels)

    context = {
        'content_types': content_types,
    }
    return render(request, 'dashboard/index.html', context)


@employee_required
def user_list_view(request):
    users = CustomUser.objects.all()
    return render(request, 'dashboard/user_list.html', {'users': users})


@employee_required
def user_add_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserCreationForm()
    return render(request, 'dashboard/user_form.html', {'form': form, 'title': 'Add User'})


@employee_required
def user_change_view(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = UserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserChangeForm(instance=user)
    return render(request, 'dashboard/user_form.html', {'form': form, 'title': 'Edit User'})


@employee_required
def model_list_view(request, app_label, model_name):
    try:
        content_type = ContentType.objects.get(app_label=app_label, model=model_name)
        model_class = content_type.model_class()
    except ContentType.DoesNotExist:
        raise Http404("Model does not exist")

    objects = model_class.objects.all()
    context = {
        'objects': objects,
        'model_name': model_name,
        'app_label': app_label,
    }
    return render(request, 'dashboard/model_list.html', context)


@employee_required
def model_form(request, app_label, model_name, object_id=None):
    try:
        content_type = ContentType.objects.get(app_label=app_label, model=model_name)
        model_class = content_type.model_class()
    except ContentType.DoesNotExist:
        raise Http404("Model does not exist")

    if object_id:
        instance = get_object_or_404(model_class, id=object_id)
    else:
        instance = None

    ModelForm = modelform_factory(model_class, exclude=[])

    # Customize the form to use CheckboxSelectMultiple for ManyToMany fields
    class CustomModelForm(ModelForm):
        class Meta(ModelForm.Meta):
            widgets = {}
            for field in model_class._meta.get_fields():
                if field.many_to_many:
                    widgets[field.name] = forms.CheckboxSelectMultiple()

    if request.method == "POST":
        form = CustomModelForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('model_list', app_label=app_label, model_name=model_name)
    else:
        form = CustomModelForm(instance=instance)

    context = {
        'form': form,
        'model_name': model_name,
        'app_label': app_label,
    }
    return render(request, 'dashboard/model_form.html', context)
