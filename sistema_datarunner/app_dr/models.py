from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O usuário deve ter um e-mail')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.date_joined = timezone.now()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data_nascimento = models.DateField(null=True, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    altura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.user.username

# Model de testes
class Teste(models.Model):
    TIPOS_TESTE = [
        ('3k', '3 km'),
        ('12min', '12 minutos'),
    ]
    aluno = models.ForeignKey(User, on_delete=models.CASCADE)  # Relaciona teste x aluno
    data_teste = models.DateField()
    tipo_teste = models.CharField(max_length=5, choices=TIPOS_TESTE)
    tempo = models.CharField(max_length=5, null=True, blank=True)  # Usando CharField para tempo como string
    distancia = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # Para testes de 12min
    bpm = models.IntegerField()  # Batimentos cardíacos
    pace = models.CharField(max_length=10, blank=True)

    def calcular_pace(self):
        if self.tipo_teste == '3k' and self.tempo:
            # Cálculo de pace para teste de 3k
            minutos, segundos = map(int, self.tempo.split(':'))
            total_minutos = minutos + (segundos / 60)
            pace = total_minutos / 3
            return f'{int(pace // 1)}:{int((pace % 1) * 60):02d} min/km'
        elif self.tipo_teste == '12min' and self.distancia:
            # Cálculo de pace para teste de 12min
            tempo_minutos = 12
            pace = tempo_minutos / self.distancia
            return f'{int(pace // 1)}:{int((pace % 1) * 60):02d} min/km'
        return None

    def save(self, *args, **kwargs):
        self.pace = self.calcular_pace()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Teste de {self.tipo_teste} - {self.aluno.first_name}'
