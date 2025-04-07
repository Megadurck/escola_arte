from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


cpf_validator = RegexValidator(
    regex=r'^\d{11}$',
    message="O CPF deve conter exatamente 11 dígitos numéricos."
)

telefone_validator = RegexValidator(
    regex=r'^\d{10,11}$',
    message="O telefone deve conter entre 10 e 11 dígitos numéricos."
)

class Curso(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(default='')
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    imagem = models.ImageField(upload_to='cursos/', null=True, blank=True)
    vagas_total = models.IntegerField(default=30)
    
    def __str__(self):
        return self.nome
    
    def vagas_disponiveis(self):
        total_vagas = sum(turma.vagas for turma in self.turmas.all())
        total_inscritos = sum(turma.inscricaoturma_set.count() for turma in self.turmas.all())
        return total_vagas - total_inscritos

class Turma(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='turmas')
    nome = models.CharField(max_length=50)  # Ex: "Turma 1", "Turma 2"
    dia_semana = models.CharField(max_length=20)  # Ex: "Segunda-feira", "Terça-feira"
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    vagas = models.IntegerField(default=30)
    vagas_originais = models.IntegerField(default=30, help_text="Número original de vagas da turma")
    
    class Meta:
        unique_together = ['curso', 'dia_semana', 'horario_inicio', 'horario_fim']
    
    def __str__(self):
        return f"{self.curso.nome} - {self.nome} ({self.dia_semana})"
    
    def vagas_disponiveis(self):
        return self.vagas - self.inscricaoturma_set.count()
    
    def save(self, *args, **kwargs):
        # Se for uma nova turma, define o número original de vagas
        if not self.pk:
            self.vagas_originais = self.vagas
        super().save(*args, **kwargs)

class Inscricao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nome_completo = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11, unique=True)
    data_nascimento = models.DateField()
    telefone_whatsapp = models.CharField(max_length=11)
    rua = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    data_inscricao = models.DateTimeField(auto_now_add=True)
    turmas = models.ManyToManyField(Turma, through='InscricaoTurma')
    
    def __str__(self):
        return f"{self.nome_completo} - {self.cpf}"
        
    def delete(self, *args, **kwargs):
        # Obtém todas as turmas associadas à inscrição
        inscricoes_turma = InscricaoTurma.objects.filter(inscricao=self)
        
        # Atualiza o contador de vagas para cada turma
        for inscricao_turma in inscricoes_turma:
            turma = inscricao_turma.turma
            turma.vagas = turma.vagas + 1
            turma.save()
            print(f"Vagas atualizadas após deletar inscrição: {turma.vagas}")
            
        # Chama o método delete da classe pai
        super().delete(*args, **kwargs)

class InscricaoTurma(models.Model):
    inscricao = models.ForeignKey(Inscricao, on_delete=models.CASCADE)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    data_inscricao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['inscricao', 'turma']
    
    def save(self, *args, **kwargs):
        if self.turma.vagas_disponiveis() <= 0:
            raise ValidationError('Não há vagas disponíveis para esta turma.')
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Atualiza o contador de vagas antes de deletar
        turma = self.turma
        super().delete(*args, **kwargs)
        # Atualiza o contador de vagas após deletar
        turma.refresh_from_db()
        turma.vagas = turma.vagas + 1
        turma.save()
        print(f"Vagas atualizadas após deletar: {turma.vagas}")

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
