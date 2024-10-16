from re import search

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import UserProfile, Teste, Aluno
from .forms import FormRegistroUsuario, TesteForm, AlunoForm


# Verifica se o usuário é admin
def is_admin(user):
    return user.is_staff

# Tela para quem tem perfil de admin
@user_passes_test(is_admin)
def admin_dashboard(request):
    testes = Teste.objects.all()
    filtro_tipo_teste = request.GET.get('filtro_tipo_teste')
    busca_nome_aluno = request.GET.get('busca_nome_aluno')

    if filtro_tipo_teste:
        testes = testes.filter(tipo_teste = filtro_tipo_teste)
    if busca_nome_aluno:
        testes = testes.filter(aluno__user__first__name__icontatins=busca_nome_aluno)

    return render(request, 'admin_dashboard.html', {'testes': testes})

# Cadastrar teste
@user_passes_test(is_admin)
def cadastrar_teste(request):
    if request.method == 'POST':
        formulario = TesteForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Teste cadastrado com sucesso!')
            return redirect('admin_dashboard')
    else:
        formulario = TesteForm()
    return render(request,'cadastrar_teste.html', {'formulario': formulario})

# Editar teste
@user_passes_test(is_admin)
def editar_teste(request, teste_id):
    teste = get_object_or_404(Teste, id=teste_id)
    if request.method == 'POST':
        formulario = TesteForm(request.POST, instance=teste)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Teste atualizado com sucesso')
            return redirect('admin_dashboard')
    else:
        formulario = TesteForm(instance=teste)
    return render(request, 'editar_teste.html', {'formulario', formulario})

# Excluir teste
@user_passes_test(is_admin)
def excluir_teste(request, teste_id):
    teste = get_object_or_404(Teste, id=teste_id)
    teste.delete()
    messages.success(request, 'Teste excluído com sucesso.')
    return redirect('admin_dashboard')

# Cadastrar aluno
@user_passes_test(is_admin)
def cadastrar_aluno(request):
    if request.method == 'POST':
        formulario = AlunoForm(request.POST)
        if formulario.is_valid():
            # Criando usuário
            nome_completo = formulario.cleaned_data['nome_completo']
            email = formulario.cleaned_data['email']
            senha = formulario.cleaned_data['senha']

            primeiro_nome = nome_completo.split(' ')[0]
            ultimo_nome = ' '.join(nome_completo.split(' ')[1:])

            # Enviando para BD
            user = User.objects.create_user(
                username = email,
                email = email,
                password = senha,
                first_name = primeiro_nome,
                last_name = ultimo_nome
            )

            aluno = formulario.save(commit=False)
            aluno.user = user # Associando o aluno ao usuário criado
            aluno.save()

            messages.success(request, 'Aluno cadastrado com sucesso!')
            return redirect('admin_dashboard')
    else:
        formulario = AlunoForm()
    return render(request, 'cadastrar_aluno.html', {'formulario': formulario})

# view da homepage
def home(request):
    return render(request, 'home.html')

# view para registro de usuário
def registro(request):
    if request.method == 'POST':
        formulario = FormRegistroUsuario(request.POST)
        if formulario.is_valid():
            user            = formulario.save()
            nome_completo   = formulario.cleaned_data.get('nome_completo')

            user.first_name = nome_completo.split(' ')[0]
            user.last_name  = ' '.join(nome_completo.split(' ')[1:])
            user.save()

            #Define como usuário comum
            UserProfile.objects.create(user=user, is_admin=False)

            login(request, user)
            return redirect('login')
    else:
        formulario = FormRegistroUsuario()

    return render(request, 'registro.html', {'formulario': formulario})

# Tela de login
def login_usuario(request):
    if request.method == 'POST':
        formulario = AuthenticationForm(request, data=request.POST)
        if formulario.is_valid():
            username    = formulario.cleaned_data.get('username')
            password    = formulario.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.first_name}')

                # Checa se o usuário é admin
                if user.is_staff:
                    return redirect('admin_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
        else:
            messages.error(request, 'Formulário inválido. Verifique os dados informados.')
    else:
        formulario = AuthenticationForm()

    return render(request, 'login.html', {'formulario': formulario})

# Mensagem de logout
def logout(request):
    logout(request)
    messages.info(request, 'Sessão encerrada com sucesso.')
    return redirect('login') #redirecionando para área de login

