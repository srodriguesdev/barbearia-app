from django.db import models

# Create your models here.
class Barbeiro(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, blank=True)
    especialidades = models.CharField(max_length=100, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    duracao = models.PositiveBigIntegerField()
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome