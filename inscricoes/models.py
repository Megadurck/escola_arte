from django.db import models
from django.db import transaction
from django.core.validators import FileExtensionValidator, RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _



cpf_validator = RegexValidator(
    regex=r'^\d{11}$',
    message="O CPF deve conter exatamente 11 dígitos numéricos."
)

telefone_validator = RegexValidator(
    regex=r'^\d{10,11}$',
    message="O telefone deve conter entre 10 e 11 dígitos numéricos."
)


def ano_letivo_atual():
    return timezone.now().year

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
    ano_letivo = models.IntegerField(
        default=ano_letivo_atual,
        validators=[MinValueValidator(2000), MaxValueValidator(2100)],
        db_index=True,
    )
    nome = models.CharField(max_length=50)  # Ex: "Turma 1", "Turma 2"
    dia_semana = models.CharField(max_length=20)  # Ex: "Segunda-feira", "Terça-feira"
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    vagas = models.IntegerField(default=30)
    vagas_originais = models.IntegerField(default=30, help_text="Número original de vagas da turma")
    
    class Meta:
        unique_together = ['curso', 'ano_letivo', 'dia_semana', 'horario_inicio', 'horario_fim']
    
    def __str__(self):
        return f"{self.curso.nome} - {self.nome} ({self.dia_semana}/{self.ano_letivo})"
    
    def save(self, *args, **kwargs):
        # Se for uma nova turma, define o número original de vagas
        if not self.pk:
            self.vagas_originais = self.vagas
        super().save(*args, **kwargs)

    def vagas_disponiveis(self):
        """Retorna o número real de vagas disponíveis"""
        # Força uma nova consulta ao banco para obter o número atual de inscritos
        self.refresh_from_db()
        inscritos = self.inscricaoturma_set.count()
        vagas_disponiveis = max(0, self.vagas_originais - inscritos)
        
        # Atualiza o campo vagas para manter a consistência
        if self.vagas != vagas_disponiveis:
            self.vagas = vagas_disponiveis
            self.save(update_fields=['vagas'])
            
        return vagas_disponiveis

    def listar_encontros(self):
        """Compatibilidade: usa encontros normalizados quando existirem."""
        encontros_qs = self.encontros.all().order_by('dia_semana', 'horario_inicio')
        if encontros_qs.exists():
            return encontros_qs
        return [
            EncontroTurma(
                turma=self,
                dia_semana=self.dia_semana,
                horario_inicio=self.horario_inicio,
                horario_fim=self.horario_fim,
            )
        ]


class EncontroTurma(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='encontros')
    dia_semana = models.CharField(max_length=20)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()

    class Meta:
        unique_together = ['turma', 'dia_semana', 'horario_inicio', 'horario_fim']
        ordering = ['dia_semana', 'horario_inicio']

    def __str__(self):
        return (
            f"{self.turma.curso.nome} - {self.turma.nome} - "
            f"{self.dia_semana} ({self.horario_inicio} - {self.horario_fim})"
        )

class Inscricao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nome_completo = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11, validators=[cpf_validator], db_index=True)
    ano_letivo = models.IntegerField(
        default=ano_letivo_atual,
        validators=[MinValueValidator(2000), MaxValueValidator(2100)],
        db_index=True,
    )
    data_nascimento = models.DateField()
    telefone_whatsapp = models.CharField(max_length=11)
    rua = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    data_inscricao = models.DateTimeField(auto_now_add=True)
    turmas = models.ManyToManyField(Turma, through='InscricaoTurma')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cpf', 'ano_letivo'], name='uniq_inscricao_cpf_ano_letivo')
        ]
    
    def __str__(self):
        return f"{self.nome_completo} - {self.cpf} ({self.ano_letivo})"
        
    def delete(self, *args, **kwargs):
        # Não precisa mais atualizar o contador de vagas pois agora usamos vagas_originais
        super().delete(*args, **kwargs)

class InscricaoTurma(models.Model):
    inscricao = models.ForeignKey(Inscricao, on_delete=models.CASCADE)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    data_inscricao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['inscricao', 'turma']
    
    def save(self, *args, **kwargs):
        if self.inscricao.ano_letivo != self.turma.ano_letivo:
            raise ValidationError('A inscrição e a turma devem pertencer ao mesmo ano letivo.')

        if self.pk:
            return super().save(*args, **kwargs)

        # Serializa a criação por turma para não estourar vagas em acessos simultâneos.
        with transaction.atomic():
            turma = Turma.objects.select_for_update().get(pk=self.turma_id)
            inscritos = InscricaoTurma.objects.filter(turma=turma).count()

            if inscritos >= turma.vagas_originais:
                raise ValidationError('Não há vagas disponíveis para esta turma.')

            self.turma = turma
            super().save(*args, **kwargs)

            vagas_restantes = max(0, turma.vagas_originais - (inscritos + 1))
            if turma.vagas != vagas_restantes:
                Turma.objects.filter(pk=turma.pk).update(vagas=vagas_restantes)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        # Não precisa atualizar o contador de vagas pois agora usamos vagas_originais

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

class DocumentoTransparencia(models.Model):
    CATEGORIA_CHOICES = [
        ("institucional", "Institucional"),
        ("financeiro", "Financeiro"),
        ("regularidade", "Regularidade"),
        ("administrativo", "Administrativo"),
    ]

    titulo = models.CharField("Título", max_length=200)
    categoria = models.CharField("Categoria", max_length=20, choices=CATEGORIA_CHOICES)
    descricao = models.TextField("Descrição", blank=True)
    arquivo = models.FileField(
        "Arquivo",
        upload_to='documentos_transparencia/',
        validators=[FileExtensionValidator(['pdf'])],
    )
    ano_referencia = models.IntegerField("Ano de Referência", blank=True, null=True)
    data_publicacao = models.DateField("Data de Publicação", blank=True, null=True)
    ativo = models.BooleanField("Ativo", default=True)
    ordem = models.PositiveIntegerField("Ordem na tela", default=0)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        ordering = ["ordem", "-data_publicacao", "titulo"]
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"

    def __str__(self):
        return self.titulo
