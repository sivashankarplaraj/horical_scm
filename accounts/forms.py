from django import forms
from django.contrib.auth.forms import AuthenticationForm
from masters.models import Branch


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        })
    )


class BranchSelectionForm(forms.Form):
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        empty_label='-- Select Branch --',
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            if user.is_superuser:
                self.fields['branch'].queryset = Branch.objects.filter(is_active=True)
            else:
                self.fields['branch'].queryset = user.branches.filter(is_active=True)
