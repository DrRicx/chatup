from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect

from .models import *
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

class UserAccountForm(UserCreationForm):
    profile_picture = forms.ImageField(required=False)
    gender = forms.ChoiceField(choices=[('MALE', 'male'), ('FEMALE', 'female')])
    student_number = forms.CharField(max_length=12, required=False)
    middle_name = forms.CharField(max_length=12, required=False)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile_picture = self.cleaned_data.get('profile_picture')
            gender = self.cleaned_data.get('gender')
            student_number = self.cleaned_data.get('student_number')
            middle_name = self.cleaned_data.get('middle_name')

            # Create Account instance regardless of whether a profile picture is provided
            Account.objects.create(
                user=user,
                profile_picture=profile_picture if profile_picture is not None else get_default_profile_image(),
                gender=gender,
                student_number=student_number,
                middle_name=middle_name
            )
        return user

class EditAccount(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=150)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = Account
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_picture']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(username=self.instance.user.username).exists():
            raise forms.ValidationError('Email addresses must be unique.')
        return email

    def save(self, commit=True):
        account = super().save(commit=False)
        if commit:
            profile_picture = self.cleaned_data.get('profile_picture')

            # Update Account instance with new profile picture if provided
            if profile_picture is not None:
                account.profile_picture = profile_picture

            # Update User instance with new user data
            user = account.user
            user.username = self.cleaned_data.get('username', user.username)  # Use existing value if not provided
            user.email = self.cleaned_data.get('email', user.email)  # Use existing value if not provided
            user.first_name = self.cleaned_data.get('first_name', user.first_name)  # Use existing value if not provided
            user.last_name = self.cleaned_data.get('last_name', user.last_name)  # Use existing value if not provided
            user.save()

            account.save()
        return account


class EditPasswordForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    class Meta:
        fields = ('old_password', 'new_password1', 'new_password2')

class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channels
        fields = ['channel_name', 'description', 'is_private', 'channel_picture']

    def save(self, commit=True):
        channel = super().save(commit=False)
        if self._user is not None:
            channel.host = self._user  # Set the host to the current user

        channel_picture = self.cleaned_data.get('channel_picture')
        if channel_picture is not None:
            channel.channel_picture = channel_picture

        if commit:
            channel.save()
        return channel

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ['category']

    def __init__(self, *args, **kwargs):
        self._channel = kwargs.pop('channel', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        category = super().save(commit=False)
        if self._channel is not None:
            category.channel_root = self._channel
        if commit:
            category.save()
        return category


class SubChannelForm(forms.ModelForm):
    class Meta:
        model = SubChannel
        fields = ['subchannel_name']

    def __init__(self, *args, **kwargs):
        self._channel = kwargs.pop('channel', None)
        self._category = kwargs.pop('category', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        subchannel = super().save(commit=False)
        if self._channel is not None:
            subchannel.category = self._category
        if commit:
            subchannel.save()
        return subchannel


class PinChannelForm(forms.Form):
    channel = forms.ModelChoiceField(queryset=Channels.objects.all())
