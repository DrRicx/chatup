from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from .models import *
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

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
