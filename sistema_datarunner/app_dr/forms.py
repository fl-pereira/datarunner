from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms

from .models import Teste, Profile, User

class FormRegistroUsuario(UserCreationForm):
    email = forms.EmailField(label="E-mail",
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'}))
    nome_completo = forms.CharField(label="Nome completo", max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Nome completo'}))
    data_nascimento = forms.DateField(label="Data de nascimento", widget=forms.DateInput(
        attrs={'class': 'form-control', 'placeholder': 'DD/MM/AAAA'}))
    peso = forms.DecimalField(label="Peso", max_digits=5, decimal_places=2,
                              widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Peso'}))
    altura = forms.DecimalField(label="Altura", max_digits=5, decimal_places=2,
                                widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Altura'}))

    class Meta:
        model = User
        fields = ['email', 'nome_completo', 'data_nascimento', 'peso', 'altura', 'password1', 'password2']
        labels = {
            'nome_completo': 'Nome completo',
            'email': 'E-mail',
            'data_nascimento': 'Data de nascimento',
            'peso': 'Peso',
            'altura': 'Altura',
            'password1': 'Senha',
            'password2': 'Confirmação de senha',
        }
        help_texts = {
            'password1': (
                "Sua senha não pode ser muito semelhante às suas outras informações pessoais.\n"
                "Sua senha deve conter pelo menos 8 caracteres.\n"
                "Sua senha não pode ser uma senha comumente usada.\n"
                "Sua senha não pode ser inteiramente numérica."
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Senha'})
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Confirmação de senha'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está registrado.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Define o email como username
        user.save()
        Profile.objects.create(
            user=user,
            data_nascimento=self.cleaned_data['data_nascimento'],
            peso=self.cleaned_data['peso'],
            altura=self.cleaned_data['altura'])
        return user
# Form para cadastro de teste
class TesteForm(forms.ModelForm):
    class Meta:
        model = Teste
        fields = ['aluno', 'data_teste', 'tipo_teste', 'tempo', 'distancia', 'bpm']
        widgets = {
            'tipo_teste': forms.Select(attrs={'class': 'form-control', 'id': 'tipo_teste'}),
            'tempo': forms.TextInput(attrs={'class': 'form-control', 'id': 'tempo', 'placeholder': 'MM:SS'}),
            'distancia': forms.NumberInput(attrs={'class': 'form-control', 'id': 'distancia', 'placeholder': 'km'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo_teste = cleaned_data.get('tipo_teste')
        tempo = cleaned_data.get('tempo')
        if tipo_teste == '3km' and tempo:
            try:
                minutos, segundos = map(int, tempo.split(':'))
                if minutos < 0 or segundos < 0 or segundos >= 60:
                    raise ValueError
                cleaned_data['tempo'] = f'{minutos:02d}:{segundos:02d}'
            except ValueError:
                self.add_error('tempo', 'Formato de tempo inválido. Use MM:SS.')
        elif tipo_teste == '12min' and not cleaned_data.get('distancia'):
            self.add_error('distancia', 'É necessário informar a distância para o teste de 12min')
        return cleaned_data

#Form para login
class CustomLoginUsuario(AuthenticationForm):

    username = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-Mail', 'autofocus': True})
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Senha'})
    )

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError("Conta desativada.", code='inactive')