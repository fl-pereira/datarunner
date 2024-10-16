from django.contrib.auth.models import User
from django.db import models
from django.db.models import TimeField

# Definindo usuário padrão
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # Cria relação do Aluno com o usuário padrão do Django
    data_nascimento = models.DateField()
    peso = models.DecimalField(max_digits=4, decimal_places=2) # Peso com 2 casas decimais
    altura = models.DecimalField(max_length=4, decimal_places=2, max_digits=5) # Altura com 2 casas decimais também

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

class Teste(models.Model):
    TIPOS_TESTE =[
        ('3k', '3 km'),
        ('12min', '12 minutos'),
    ]

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE) # Cria relação teste x aluno
    data_teste = models.DateField()
    tipo_teste = models.CharField(max_length=5, choices=TIPOS_TESTE)
    tempo = models.TimeField(null=True, blank=True) # Campo para ser preenchido quando for teste de 3km
    distancia = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True) # Campo para ser preenchido quando for teste de 12min
    bpm = models.IntegerField() # Batimentos cardíacos
    pace = models.CharField(max_length=10, blank=True)

    def calcular_pace(self):
        if self.tipo_teste == '3km' and self.tempo:
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