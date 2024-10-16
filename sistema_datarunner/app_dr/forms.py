from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Aluno, Teste


# Form para cadastro de usuário
class FormRegistroUsuario(UserCreationForm):
    email = forms.EmailField()
    nome_completo = forms.CharField(max_length=100, label='Nome completo')

    class Meta:
        model = User
        fields = ['username', 'nome_completo', 'email', 'password1', 'password2']

    def verifica_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este e-mail já está sendo utilizado')
        return email

# Form para cadastro de aluno, quando esse já é um usuário
class AlunoForm(forms.ModelForm):
    nome_completo = forms.CharField(max_length=255, label='Nome completo')
    email = forms.EmailField(label='E-mail')
    senha = forms.CharField(widget=forms.PasswordInput, label='Senha')

    class Meta:
        model = Aluno
        fields = ['data_nascimento', 'peso', 'altura']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Já existe um usuário com este e-mail')
        return email

# Form para cadastro de teste
class TesteForm(forms.ModelForm):
    class Meta:
        model = Teste
        fields = ['aluno', 'data_teste', 'tipo_teste', 'tempo', 'distancia', 'bpm']

    def clean(self):
        cleaned_data = super().clean()
        tipo_teste = cleaned_data.get('tipo_teste')

        if tipo_teste == '3km':
            if not cleaned_data.get('tempo'):
                self.add_error('tempo', 'É necessário informar o tempo para o teste de 3km')
        elif tipo_teste == '12min':
            if not cleaned_data.get('distancia'):
                self.add_error('distancia', 'É necessário informar a distância para o teste de 12min')
        return cleaned_data
