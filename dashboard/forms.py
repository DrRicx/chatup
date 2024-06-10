from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from account.models import *

User = get_user_model()

class LoginForm(forms.Form):
    user_number = forms.CharField(
        label='User Number',
        max_length=100
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput
    )

    def clean(self):
        cleaned_data = super().clean()
        user_number = cleaned_data.get('user_number')
        password = cleaned_data.get('password')

        if user_number and password:
            user = authenticate(user_number=user_number, password=password)
            if user is None:
                raise forms.ValidationError('Invalid user number or password')
        return cleaned_data

class UserCreationForm(forms.ModelForm):
    user_number = forms.CharField(max_length=12, required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    user_type = forms.ModelChoiceField(queryset=UserType.objects.all(), required=True)
    first_name = forms.CharField(max_length=12, required=True)
    last_name = forms.CharField(max_length=12, required=True)
    gender = forms.ChoiceField(choices=[('MALE', 'male'), ('FEMALE', 'female')], required=True)
    birthdate = forms.DateField(required=True)

    class Meta:
        model = CustomUser
        fields = ['user_number', 'email', 'user_type', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            profile = UserProfile(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                gender=self.cleaned_data['gender'],
                birthdate=self.cleaned_data['birthdate']
            )
            profile.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    first_name = forms.CharField(max_length=12, required=True)
    last_name = forms.CharField(max_length=12, required=True)
    gender = forms.ChoiceField(choices=[('MALE', 'male'), ('FEMALE', 'female')], required=True)
    birthdate = forms.DateField(required=True)

    class Meta:
        model = CustomUser
        fields = ['user_number', 'email', 'user_type', 'password']

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['first_name'].initial = self.instance.user_profile.first_name
            self.fields['last_name'].initial = self.instance.user_profile.last_name
            self.fields['gender'].initial = self.instance.user_profile.gender
            self.fields['birthdate'].initial = self.instance.user_profile.birthdate

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile = user.user_profile
            profile.first_name = self.cleaned_data['first_name']
            profile.last_name = self.cleaned_data['last_name']
            profile.gender = self.cleaned_data['gender']
            profile.birthdate = self.cleaned_data['birthdate']
            profile.save()
        return user