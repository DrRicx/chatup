from django import forms
from django.contrib.auth import authenticate, get_user_model

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