from django.db import models
from django.contrib.auth.models import User

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


class Agendamento(models.Model):

    STATUS_CHOICES = (
        ("confirmado", "Confirmado"),
        ("cancelado", "Cancelado"),
        ("concluido", "Concluído"),
    )

    cliente = models.ForeignKey(User, on_delete=models.PROTECT)
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.PROTECT)
    servico = models.ForeignKey(Servico, on_delete=models.PROTECT)

    data = models.DateField()
    horario = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="confirmado"
    )

    def __str__(self):
        return f"Cliente {self.cliente} - Barbeiro {self.barbeiro} - {self.data} {self.horario}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["barbeiro", "data", "horario"],
                name="unique_agendamento_barbeiro_data_horario",
            )
        ]