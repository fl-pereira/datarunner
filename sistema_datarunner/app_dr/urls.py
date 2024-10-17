from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('registro', views.registro, name='registro'),
    path('login', views.login_usuario, name='login'),
    path('user_logout', views.user_logout, name='user_logout'),
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('cadastrar_aluno', views.cadastrar_aluno, name='cadastrar_aluno'),
    path('cadastrar_teste', views.cadastrar_teste, name='cadastrar_teste'),
    path('editar_teste/<int:teste_id>', views.editar_teste, name='editar_teste'),
    path('excluir_teste/<int:teste_id>', views.excluir_teste, name='excluir_teste'),
]