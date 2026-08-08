from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.html import format_html, format_html_join
from django.urls import path, reverse
from django import forms
from django.db.models import Count, Prefetch, Q
import re
from .models import Inscricao, Curso, Funcionario, Turma, InscricaoTurma
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class InscricaoTurmaAdminForm(forms.ModelForm):
    class Meta:
        model = InscricaoTurma
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        inscricao = None
        turma = None

        inscricao_id = self.data.get('inscricao') or self.initial.get('inscricao')
        turma_id = self.data.get('turma') or self.initial.get('turma')

        if self.instance and self.instance.pk:
            inscricao = self.instance.inscricao
            turma = self.instance.turma

        if inscricao is None and inscricao_id:
            try:
                inscricao = Inscricao.objects.get(pk=inscricao_id)
            except (Inscricao.DoesNotExist, ValueError, TypeError):
                inscricao = None

        if turma is None and turma_id:
            try:
                turma = Turma.objects.get(pk=turma_id)
            except (Turma.DoesNotExist, ValueError, TypeError):
                turma = None

        if inscricao is not None:
            turmas_indisponiveis = InscricaoTurma.objects.filter(inscricao=inscricao).values_list('turma_id', flat=True)
            self.fields['turma'].queryset = Turma.objects.filter(ano_letivo=inscricao.ano_letivo).exclude(pk__in=turmas_indisponiveis)

        if turma is not None:
            inscricoes_indisponiveis = InscricaoTurma.objects.filter(turma=turma).values_list('inscricao_id', flat=True)
            self.fields['inscricao'].queryset = Inscricao.objects.filter(ano_letivo=turma.ano_letivo).exclude(pk__in=inscricoes_indisponiveis)

class TurmaInline(admin.TabularInline):
    model = Turma
    extra = 1

class InscricaoTurmaInline(admin.TabularInline):
    model = InscricaoTurma
    extra = 1
    verbose_name = "Turma"
    verbose_name_plural = "Turmas"

# Nota: os inscritos são exibidos via TurmaAdmin.inscritos_lista (campo somente leitura).
# Um TabularInline foi evitado aqui porque monta um Form/widget completo por linha,
# o que fica lento (timeout/502) em turmas com muitos inscritos.

# Registrar o modelo de Inscrição no admin
@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'cpf', 'ano_letivo', 'telefone_whatsapp', 'data_inscricao', 'turmas_display', 'adicionar_turma_link', 'gerenciar_turmas_link']
    search_fields = ['nome_completo', 'cpf']
    list_filter = ['ano_letivo', 'data_inscricao']
    list_per_page = 25
    show_full_result_count = False
    autocomplete_fields = ['usuario']
    inlines = [InscricaoTurmaInline]
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('usuario', 'nome_completo', 'cpf', 'ano_letivo', 'data_nascimento', 'telefone_whatsapp')
        }),
        ('Endereço', {
            'fields': ('rua', 'bairro', 'numero')
        }),
    )
    
    def turmas_display(self, obj):
        inscricoes_turma = getattr(obj, 'inscricoes_turma_prefetch', None)
        if inscricoes_turma is None:
            inscricoes_turma = obj.inscricaoturma_set.select_related('turma', 'turma__curso').all()

        if inscricoes_turma:
            linhas = []
            for relacao in inscricoes_turma:
                delete_url = reverse('admin:inscricoes_inscricaoturma_delete', args=[relacao.pk])
                linhas.append(
                    f"{relacao.turma.curso.nome} - {relacao.turma.nome} "
                    f"<a href='{delete_url}' style='color:#b42318; font-weight:600;'>Remover</a>"
                )
            return format_html(
                '<br>'.join(linhas)
            )
        return format_html('<span style="color: red; font-weight: bold;">Nenhuma turma</span>')
    turmas_display.short_description = 'Turmas Inscritas'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        inscricoes_turma_qs = InscricaoTurma.objects.select_related('turma', 'turma__curso')
        return qs.prefetch_related(
            Prefetch('inscricaoturma_set', queryset=inscricoes_turma_qs, to_attr='inscricoes_turma_prefetch')
        )

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        cpf_numerico = re.sub(r'\D', '', search_term or '')
        if cpf_numerico:
            queryset |= self.model.objects.filter(cpf__icontains=cpf_numerico)
        return queryset, use_distinct

    def adicionar_turma_link(self, obj):
        url = reverse('admin:inscricoes_inscricaoturma_add')
        return format_html(
            '<a class="button" href="{}?inscricao={}">Adicionar turma</a>',
            url,
            obj.pk,
        )
    adicionar_turma_link.short_description = 'Ação'

    def gerenciar_turmas_link(self, obj):
        url = reverse('admin:inscricoes_inscricaoturma_changelist')
        return format_html(
            '<a class="button" href="{}?inscricao__id__exact={}">Gerenciar turmas</a>',
            url,
            obj.pk,
        )
    gerenciar_turmas_link.short_description = 'Turmas'

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
    change_list_template = 'admin/inscricoes/turma/change_list.html'
    list_display = ['nome', 'curso', 'ano_letivo', 'dias_atuacao', 'horario_inicio', 'horario_fim', 'vagas', 'inscritos_count', 'adicionar_inscricao_link']
    list_filter = ('ano_letivo', 'curso', 'dia_semana')
    search_fields = ('nome', 'curso__nome')
    list_select_related = ('curso',)
    list_per_page = 25
    show_full_result_count = False
    readonly_fields = ('inscritos_lista',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'ajustar-vagas-violao/',
                self.admin_site.admin_view(self.ajustar_vagas_violao_view),
                name='inscricoes_turma_ajustar_vagas_violao',
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['ajustar_vagas_violao_url'] = reverse(
            'admin:inscricoes_turma_ajustar_vagas_violao'
        )
        return super().changelist_view(request, extra_context=extra_context)

    def ajustar_vagas_violao_view(self, request):
        if request.method != 'POST':
            self.message_user(
                request,
                'Use o botao da listagem para executar este ajuste.',
                level=messages.WARNING,
            )
            return HttpResponseRedirect(reverse('admin:inscricoes_turma_changelist'))

        turmas = Turma.objects.filter(
            curso__nome__icontains='viol',
        ).filter(
            Q(nome__icontains='adult')
            | Q(nome__icontains='aduldo')
            | Q(nome__icontains='infantil')
        ).annotate(inscritos_total=Count('inscricaoturma'))

        total = turmas.count()
        atualizadas = 0
        for turma in turmas:
            vagas_disponiveis_novas = max(0, 40 - turma.inscritos_total)
            if turma.vagas == vagas_disponiveis_novas and turma.vagas_originais == 40:
                continue

            turma.vagas = vagas_disponiveis_novas
            turma.vagas_originais = 40
            turma.save(update_fields=['vagas', 'vagas_originais'])
            atualizadas += 1

        if total == 0:
            self.message_user(
                request,
                'Nenhuma turma de Violao Adulto/Infantil foi encontrada.',
                level=messages.WARNING,
            )
        else:
            self.message_user(
                request,
                f'Ajuste concluido. Turmas encontradas: {total}. Turmas atualizadas: {atualizadas}.',
                level=messages.SUCCESS,
            )

        return HttpResponseRedirect(reverse('admin:inscricoes_turma_changelist'))
    
    def inscritos_count(self, obj):
        return getattr(obj, 'inscritos_total', 0)
    inscritos_count.short_description = 'Número de Inscritos'

    def dias_atuacao(self, obj):
        encontros = getattr(obj, 'encontros_prefetch', None)
        if encontros is None:
            encontros = obj.encontros.all()

        if encontros:
            dias = sorted({encontro.dia_semana for encontro in encontros})
            return ', '.join(dias)

        return obj.dia_semana
    dias_atuacao.short_description = 'Dias de Atuação'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('curso').prefetch_related(
            Prefetch('encontros', to_attr='encontros_prefetch')
        ).annotate(inscritos_total=Count('inscricaoturma'))

    def adicionar_inscricao_link(self, obj):
        url = reverse('admin:inscricoes_inscricaoturma_add')
        return format_html(
            '<a class="button" href="{}?turma={}">Adicionar inscrição</a>',
            url,
            obj.pk,
        )
    adicionar_inscricao_link.short_description = 'Ação'

    def inscritos_lista(self, obj):
        if not obj.pk:
            return '-'
        # ordem de inscrição (mais antigo primeiro), não alfabética
        relacoes = InscricaoTurma.objects.filter(turma=obj).select_related('inscricao').order_by('data_inscricao', 'id')
        if not relacoes:
            return format_html('<span style="color: red; font-weight: bold;">Nenhum inscrito</span>')

        linhas = format_html_join(
            '',
            '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td>'
            "<td><a href='{}' style='color:#b42318; font-weight:600;'>Remover</a></td></tr>",
            (
                (
                    posicao,
                    relacao.inscricao.nome_completo,
                    relacao.inscricao.telefone_whatsapp,
                    relacao.inscricao.cpf,
                    reverse('admin:inscricoes_inscricaoturma_delete', args=[relacao.pk]),
                )
                for posicao, relacao in enumerate(relacoes, start=1)
            ),
        )
        return format_html(
            "<table style='border-collapse: collapse; width: 100%;'>"
            "<thead><tr>"
            "<th style='text-align:left; padding:4px 8px;'>#</th>"
            "<th style='text-align:left; padding:4px 8px;'>Nome</th>"
            "<th style='text-align:left; padding:4px 8px;'>Telefone</th>"
            "<th style='text-align:left; padding:4px 8px;'>CPF</th>"
            "<th style='text-align:left; padding:4px 8px;'>Ação</th>"
            "</tr></thead><tbody>{}</tbody></table>",
            linhas,
        )
    inscritos_lista.short_description = 'Inscritos'

# Registrar o modelo de Funcionario no admin
@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cargo', 'email', 'telefone']
    search_fields = ('nome', 'email')
    list_filter = ('cargo',)
    list_per_page = 25
    show_full_result_count = False
    filter_horizontal = ('cursos',)

# Personalização do UserAdmin
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'superuser_indicator', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    ordering = ('-date_joined',)
    list_per_page = 25
    show_full_result_count = False
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

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
    form = InscricaoTurmaAdminForm
    list_display = ['inscricao', 'turma', 'data_inscricao']
    list_filter = ['turma__ano_letivo', 'turma', 'data_inscricao']
    search_fields = ['inscricao__nome_completo', 'turma__nome']
    readonly_fields = ['data_inscricao']
    autocomplete_fields = ['inscricao', 'turma']
    list_select_related = ['inscricao', 'turma', 'turma__curso']
    list_per_page = 25
    show_full_result_count = False


