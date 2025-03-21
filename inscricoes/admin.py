from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Inscricao, Curso, Funcionario
from django.contrib.auth.models import User

# Definir o Inline para Inscrição
class InscricaoInline(admin.TabularInline):
    model = Inscricao.cursos.through  # Usa o modelo intermediário ManyToMany
    extra = 0

# Registrar o modelo de Inscrição no admin
@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'cpf', 'rua', 'bairro', 'numero', 'telefone_whatsapp', 'data_nascimento', 'painel_link']
    search_fields = ['nome_completo', 'cpf']
    list_filter = ['data_nascimento']

    # Adiciona um botão/link para acessar o painel
    def painel_link(self, obj):
        url = reverse('inscricoes:dashboard')  # Link para o painel
        return format_html('<a href="{}" target="_blank">Ir para o Painel</a>', url)

    painel_link.short_description = 'Acessar Painel'

# Registrar o modelo de Curso no admin
@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    inlines = [InscricaoInline]

# Registrar o modelo de Funcionario no admin
@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cargo', 'email', 'telefone']
    search_fields = ['nome', 'cargo']
    list_filter = ['cargo']

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
