from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .backends import EmailBackend

from .models import Teste
from .forms import FormRegistroUsuario, TesteForm, CustomLoginUsuario

# Verifica se o usuário é admin
def is_admin(user):
    return user.is_staff

# view da homepage
def home(request):
    return render(request, 'home.html')

def admin_dashboard(request):
    # Se o usuário for administrador, ele pode ver todos os testes
    if request.user.is_staff:
        testes = Teste.objects.all()
    else:
        # Usuários comuns veem apenas seus próprios testes
        testes = Teste.objects.filter(aluno=request.user)

    # Aplicando os filtros, se existirem
    filtro_tipo_teste = request.GET.get('filtro_tipo_teste')
    busca_nome_aluno = request.GET.get('busca_nome_aluno')

    if filtro_tipo_teste:
        testes = testes.filter(tipo_teste=filtro_tipo_teste)

    if busca_nome_aluno:
        # Administradores podem buscar alunos por nome
        if request.user.is_staff:
            testes = testes.filter(aluno__user__first_name__icontains=busca_nome_aluno)

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
    return render(request, 'editar_teste.html', {'formulario': formulario})

# Excluir teste
@user_passes_test(is_admin)
def excluir_teste(request, teste_id):
    teste = get_object_or_404(Teste, id=teste_id)
    teste.delete()
    messages.success(request, 'Teste excluído com sucesso.')
    return redirect('admin_dashboard')

# view para registro de usuário
def registro(request):
    if request.method == 'POST':
        formulario = FormRegistroUsuario(request.POST)
        if formulario.is_valid():
            # Cria e salva o usuário
            user = formulario.save()
            # Autentica o usuário
            email = formulario.cleaned_data.get('email')
            password = formulario.cleaned_data.get('password1')
            user = authenticate(request, email=email, password=password, backend='app_dr.backends.EmailBackend')
            if user is not None:
                login(request, user, backend='app_dr.backends.EmailBackend')
                messages.success(request, f'Bem-vindo, {user.first_name}')
                # Redireciona o usuário para a página de dashboard
                return redirect('admin_dashboard')
    else:
        formulario = FormRegistroUsuario()
    return render(request, 'registro.html', {'formulario': formulario})

# Tela de login
def login_usuario(request):
    if request.method == 'POST':
        formulario = CustomLoginUsuario(request, data=request.POST)
        if formulario.is_valid():
            email = formulario.cleaned_data.get('username')
            password = formulario.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user, backend='app_dr.backends.EmailBackend')
                messages.success(request, f'Bem-vindo, {user.first_name}')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
        else:
            messages.error(request, 'Formulário inválido. Verifique os dados informados.')
    else:
        formulario = CustomLoginUsuario()
    return render(request, 'login.html', {'formulario': formulario})

# Mensagem de logout
def user_logout(request):
    logout(request)
    messages.info(request, 'Sessão encerrada com sucesso.')
    return redirect('login') #redirecionando para área de login

