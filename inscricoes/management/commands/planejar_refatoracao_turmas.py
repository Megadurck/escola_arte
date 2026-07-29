from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Count

from inscricoes.models import Turma, InscricaoTurma


class Command(BaseCommand):
    help = (
        "Audita redundancia de turmas por dia e projeta impacto da refatoracao "
        "para turma logica + encontros (dry-run, sem alterar dados)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--ano",
            type=int,
            default=int(getattr(settings, "ANO_LETIVO_ATUAL", 0) or 0),
            help="Ano letivo para auditoria (padrao: ANO_LETIVO_ATUAL).",
        )

    def handle(self, *args, **options):
        ano = options["ano"]
        if not ano:
            self.stdout.write(
                self.style.ERROR("Informe um ano valido com --ano ou ANO_LETIVO_ATUAL.")
            )
            return

        self.stdout.write(self.style.WARNING(f"Auditoria em dry-run para o ano {ano}"))

        grupos = (
            Turma.objects
            .filter(ano_letivo=ano)
            .values("curso_id", "curso__nome", "nome", "horario_inicio", "horario_fim")
            .annotate(total_turmas=Count("id"))
            .order_by("curso__nome", "nome", "horario_inicio")
        )

        total_grupos_multidias = 0
        total_relacoes_atuais = 0
        total_relacoes_pos_refatoracao = 0

        for grupo in grupos:
            if grupo["total_turmas"] <= 1:
                continue

            total_grupos_multidias += 1
            turmas_ids = list(
                Turma.objects.filter(
                    curso_id=grupo["curso_id"],
                    ano_letivo=ano,
                    nome=grupo["nome"],
                    horario_inicio=grupo["horario_inicio"],
                    horario_fim=grupo["horario_fim"],
                ).values_list("id", flat=True)
            )

            relacoes_qs = InscricaoTurma.objects.filter(turma_id__in=turmas_ids)
            relacoes_atuais = relacoes_qs.count()
            unicos = relacoes_qs.values("inscricao_id").distinct().count()

            total_relacoes_atuais += relacoes_atuais
            total_relacoes_pos_refatoracao += unicos

            self.stdout.write(
                (
                    f"- {grupo['curso__nome']} | {grupo['nome']} | "
                    f"{grupo['horario_inicio']} - {grupo['horario_fim']} | "
                    f"dias={grupo['total_turmas']} | "
                    f"relacoes_atual={relacoes_atuais} | "
                    f"inscritos_unicos={unicos} | "
                    f"reducao_prevista={relacoes_atuais - unicos}"
                )
            )

        self.stdout.write("\nResumo:")
        self.stdout.write(f"- Grupos multi-dia encontrados: {total_grupos_multidias}")
        self.stdout.write(f"- Relacoes atuais (grupos multi-dia): {total_relacoes_atuais}")
        self.stdout.write(
            f"- Relacoes estimadas pos-refatoracao: {total_relacoes_pos_refatoracao}"
        )
        self.stdout.write(
            f"- Reducao estimada de redundancia: "
            f"{total_relacoes_atuais - total_relacoes_pos_refatoracao}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Dry-run concluido. Nenhum dado foi alterado."
            )
        )
