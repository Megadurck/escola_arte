from django.db import models
from django.core.validators import RegexValidator


cpf_validator = RegexValidator(
    regex=r'^\d{11}$',
    message="O CPF deve conter exatamente 11 dígitos numéricos."
)

telefone_validator = RegexValidator(
    regex=r'^\d{10,11}$',
    message="O telefone deve conter entre 10 e 11 dígitos numéricos."
)

class Curso(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField()

    def __str__(self):
        return self.nome
    

class Inscricao(models.Model):
    nome_completo = models.CharField(max_length=200)
    cpf = models.CharField(max_length=11, unique=True, validators=[cpf_validator])
    rua = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    telefone_whatsapp = models.CharField(max_length=15, validators=[telefone_validator])
    data_nascimento = models.DateField()
    cursos = models.ManyToManyField(Curso, related_name='inscricoes')
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE,)
    data_inscricao = models.DateTimeField(auto_now_add=True)  # Adicionando esse campo


    class Meta:
        unique_together = ('usuario',)  # Isso vai garantir que o usuário só possa se inscrever uma vez

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
    cursos = models.ManyToManyField(Curso)

    def get_cargo_display(self):
        return dict(self.TIPO).get(self.cargo, "Desconhecido")

    def __str__(self):
        return f"{self.nome} - {self.get_cargo_display()}"
