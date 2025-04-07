from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Inscricao, Curso, Funcionario, Turma, InscricaoTurma
from django.contrib.auth.models import User

class TurmaInline(admin.TabularInline):
    model = Turma
    extra = 1

class InscricaoTurmaInline(admin.TabularInline):
    model = InscricaoTurma
    extra = 1
    verbose_name = "Turma"
    verbose_name_plural = "Turmas"

class InscritosTurmaInline(admin.TabularInline):
    model = InscricaoTurma
    extra = 0
    readonly_fields = ('inscricao_info', 'data_inscricao')
    can_delete = False
    verbose_name = "Inscrito"
    verbose_name_plural = "Inscritos"
    
    def has_add_permission(self, request, obj=None):
        return False
        
    def inscricao_info(self, obj):
        inscricao = obj.inscricao
        return format_html(
            '<strong>Nome:</strong> {}<br>'
            '<strong>Telefone:</strong> {}<br>'
            '<strong>CPF:</strong> {}',
            inscricao.nome_completo,
            inscricao.telefone_whatsapp,
            inscricao.cpf
        )
    inscricao_info.short_description = 'Informações do Inscrito'

# Registrar o modelo de Inscrição no admin
@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'cpf', 'telefone_whatsapp', 'data_inscricao', 'turmas_display']
    search_fields = ['nome_completo', 'cpf']
    list_filter = ['data_inscricao']
    inlines = [InscricaoTurmaInline]
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('usuario', 'nome_completo', 'cpf', 'data_nascimento', 'telefone_whatsapp')
        }),
        ('Endereço', {
            'fields': ('rua', 'bairro', 'numero')
        }),
    )
    
    def turmas_display(self, obj):
        # Obtém as turmas através da relação InscricaoTurma
        inscricoes_turma = InscricaoTurma.objects.filter(inscricao=obj).select_related('turma', 'turma__curso')
        if inscricoes_turma:
            return format_html(
                '<br>'.join([f"{insc.turma.curso.nome} - {insc.turma.nome}" for insc in inscricoes_turma])
            )
        return format_html('<span style="color: red; font-weight: bold;">Nenhuma turma</span>')
    turmas_display.short_description = 'Turmas Inscritas'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('inscricaoturma_set__turma', 'inscricaoturma_set__turma__curso')

# Registrar o modelo de Curso no admin
@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao', 'valor', 'vagas_total']
    search_fields = ('nome',)
    inlines = [TurmaInline]
    list_editable = ['vagas_total']

# Registrar o modelo de Turma no admin
@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'curso', 'dia_semana', 'horario_inicio', 'horario_fim', 'vagas', 'inscritos_count']
    list_filter = ('curso', 'dia_semana')
    search_fields = ('nome', 'curso__nome')
    inlines = [InscritosTurmaInline]
    
    def inscritos_count(self, obj):
        return obj.inscricaoturma_set.count()
    inscritos_count.short_description = 'Número de Inscritos'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('inscricaoturma_set__inscricao')

# Registrar o modelo de Funcionario no admin
@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cargo', 'email', 'telefone']
    search_fields = ('nome', 'email')
    list_filter = ('cargo',)
    filter_horizontal = ('cursos',)

# Personalização do UserAdmin
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'superuser_indicator')

    def superuser_indicator(self, obj):
        if obj.is_superuser:
            return format_html('<span style="color: green; font-weight: bold;">Superuser</span>')
        return format_html('<span style="color: red;">Usuário Comum</span>')
    
    superuser_indicator.short_description = 'Status do Superuser'

# Registra o modelo User no admin com a personalização
admin.site.unregister(User)  # Desregistra a versão padrão
admin.site.register(User, UserAdmin)  # Registra a versão personalizada

# Registrar o modelo de InscricaoTurma no admin
@admin.register(InscricaoTurma)
class InscricaoTurmaAdmin(admin.ModelAdmin):
    list_display = ['inscricao', 'turma', 'data_inscricao']
    list_filter = ['turma', 'data_inscricao']
    search_fields = ['inscricao__nome_completo', 'turma__nome']
    readonly_fields = ['data_inscricao']


