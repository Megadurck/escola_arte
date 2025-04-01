from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


cpf_validator = RegexValidator(
    regex=r'^\d{11}$',
    message="O CPF deve conter exatamente 11 dígitos numéricos."
)

telefone_validator = RegexValidator(
    regex=r'^\d{10,11}$',
    message="O telefone deve conter entre 10 e 11 dígitos numéricos."
)

class Curso(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome do Curso")
    limite_inscricoes = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Número máximo de inscrições permitidas",
        null=True,  # Permite valores nulos temporariamente
        blank=True  # Permite valores em branco no formulário
    )
    descricao = models.TextField(verbose_name="Descrição", blank=True, null=True)  # Permite descrição vazia
    funcionario = models.ForeignKey('Funcionario', on_delete=models.SET_NULL, null=True, blank=True)
    horarios_disponiveis = models.ManyToManyField('HorarioCurso', blank=True, related_name='cursos')

    def __str__(self):
        return self.nome

    def vagas_disponiveis(self):
        if self.limite_inscricoes is None:
            return 0
        return self.limite_inscricoes - self.inscricoes.count()

class HorarioCurso(models.Model):
    DIAS_SEMANA = [
        ('segunda', 'Segunda-feira'),
        ('terca', 'Terça-feira'),
        ('quarta', 'Quarta-feira'),
        ('quinta', 'Quinta-feira'),
        ('sexta', 'Sexta-feira'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo')
    ]

    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.CharField(max_length=20, choices=DIAS_SEMANA, verbose_name="Dia da semana")
    horario_inicio = models.TimeField(verbose_name="Horário de início")
    horario_fim = models.TimeField(verbose_name="Horário de término")
    vagas_disponiveis = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Número de vagas disponíveis neste horário"
    )

    class Meta:
        verbose_name = "Horário do Curso"
        verbose_name_plural = "Horários dos Cursos"
        unique_together = ['curso', 'dia_semana', 'horario_inicio', 'horario_fim']

    def __str__(self):
        return f"{self.curso.nome} - {self.get_dia_semana_display()} ({self.horario_inicio} - {self.horario_fim})"

class Inscricao(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_completo = models.CharField(max_length=200)
    cpf = models.CharField(max_length=11, unique=True, validators=[cpf_validator])
    rua = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    telefone_whatsapp = models.CharField(max_length=15, validators=[telefone_validator])
    data_nascimento = models.DateField()
    cursos = models.ManyToManyField(Curso, related_name='inscricoes')
    horarios_selecionados = models.ManyToManyField(HorarioCurso, related_name='inscricoes')
    data_inscricao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome_completo

class Funcionario(models.Model):
    TIPO = (
        ('professor', 'Professor'),
        ('coordenador', 'Coordenador'),
        ('administrativo', 'Administrativo'),
    )
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=15, choices=TIPO)
    email = models.EmailField()
    telefone = models.CharField(max_length=11, validators=[telefone_validator])
    cursos = models.ManyToManyField(Curso, related_name='funcionarios')

    def get_cargo_display(self):
        return dict(self.TIPO).get(self.cargo, "Desconhecido")

    def __str__(self):
        return f"{self.nome} - {self.get_cargo_display()}"
