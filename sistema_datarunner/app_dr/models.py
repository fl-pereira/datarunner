from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models

# Model de usuários
class UserManager(BaseUserManager):
    def cria_usuario(self, email, password=None, **campos_extras):
        if not email:
            raise ValueError('O usuário deve ter um e-mail')
        email = self.normalize_email(email)
        user = self.model(email=email, **campos_extras)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def cria_super_usuario(self, email, password=None, **campos_extras):
        campos_extras.setdefault('is_staff', True)
        campos_extras.setdefault('is_superuser', True)
        return self.cria_usuario(email, password, **campos_extras)

class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

# Model do aluno, associado ao usuário
class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Relaciona o Aluno ao User
    data_nascimento = models.DateField()
    peso = models.DecimalField(max_digits=4, decimal_places=2)  # Peso com 2 casas decimais
    altura = models.DecimalField(decimal_places=2, max_digits=5)  # Corrigido: sem max_length

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

# Model de testes
class Teste(models.Model):
    TIPOS_TESTE = [
        ('3k', '3 km'),
        ('12min', '12 minutos'),
    ]

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)  # Relaciona teste x aluno
    data_teste = models.DateField()
    tipo_teste = models.CharField(max_length=5, choices=TIPOS_TESTE)
    tempo = models.TimeField(null=True, blank=True)  # Para testes de 3km
    distancia = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # Para testes de 12min
    bpm = models.IntegerField()  # Batimentos cardíacos
    pace = models.CharField(max_length=10, blank=True)

    def calcular_pace(self):
        if self.tipo_teste == '3k' and self.tempo:
            # Cálculo de pace para teste de 3k
            tempo_minutos = (self.tempo.hour * 60) + self.tempo.minute + (self.tempo.second / 60)
            pace = tempo_minutos / 3
            return f'{pace:.2f} min/km'
        elif self.tipo_teste == '12min' and self.distancia:
            pace = 12 / (self.distancia / 1000)
            return f'{pace:.2f} min/km'
        return None

    def save(self, *args, **kwargs):
        self.pace = self.calcular_pace()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Teste de {self.tipo_teste} - {self.aluno.user.first_name}'