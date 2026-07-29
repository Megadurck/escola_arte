from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count

from inscricoes.models import EncontroTurma, InscricaoTurma, Turma


class Command(BaseCommand):
    help = (
        "Normaliza turmas com multiplos dias para turma logica unica por curso/nome/horario. "
        "Dry-run por padrao; use --confirmar para aplicar."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--ano",
            type=int,
            default=int(getattr(settings, "ANO_LETIVO_ATUAL", 0) or 0),
            help="Ano letivo alvo (padrao: ANO_LETIVO_ATUAL).",
        )
        parser.add_argument(
            "--confirmar",
            action="store_true",
            help="Aplica mudancas no banco. Sem esta flag, executa apenas simulacao.",
        )
        parser.add_argument(
            "--manter-secundarias",
            action="store_true",
            help="Mantem turmas secundarias (nao recomendado).",
        )

    @staticmethod
    def _chave_grupo(turma):
        return (
            turma.curso_id,
            turma.ano_letivo,
            (turma.nome or "").strip().lower(),
            turma.horario_inicio,
            turma.horario_fim,
        )

    def handle(self, *args, **options):
        ano = options["ano"]
        confirmar = options["confirmar"]
        manter_secundarias = options["manter_secundarias"]

        if not ano:
            self.stdout.write(self.style.ERROR("Informe um ano valido com --ano."))
            return

        modo = "APLICACAO" if confirmar else "DRY-RUN"
        self.stdout.write(self.style.WARNING(f"Modo: {modo} | Ano: {ano}"))

        turmas = list(
            Turma.objects.filter(ano_letivo=ano)
            .select_related("curso")
            .order_by("curso__nome", "nome", "horario_inicio", "id")
        )

        grupos = {}
        for turma in turmas:
            grupos.setdefault(self._chave_grupo(turma), []).append(turma)

        total_grupos_processados = 0
        total_encontros_criados = 0
        total_relacoes_movidas = 0
        total_relacoes_duplicadas_removidas = 0
        total_turmas_secundarias_removidas = 0

        for _, grupo_turmas in grupos.items():
            if len(grupo_turmas) <= 1:
                continue

            total_grupos_processados += 1
            turma_principal = min(grupo_turmas, key=lambda t: t.id)
            turmas_secundarias = [t for t in grupo_turmas if t.id != turma_principal.id]

            self.stdout.write(
                (
                    f"Grupo: {turma_principal.curso.nome} | {turma_principal.nome} | "
                    f"{turma_principal.horario_inicio}-{turma_principal.horario_fim} | "
                    f"principal={turma_principal.id} | secundarias={[t.id for t in turmas_secundarias]}"
                )
            )

            if not confirmar:
                encontros_existentes = EncontroTurma.objects.filter(turma=turma_principal).count()
                encontros_previstos = len(grupo_turmas)
                relacoes_atuais = InscricaoTurma.objects.filter(turma__in=grupo_turmas).count()
                relacoes_unicas = (
                    InscricaoTurma.objects.filter(turma__in=grupo_turmas)
                    .values("inscricao_id")
                    .distinct()
                    .count()
                )
                self.stdout.write(
                    (
                        f"  dry-run: encontros_existentes={encontros_existentes}, "
                        f"encontros_esperados={encontros_previstos}, "
                        f"relacoes_atual={relacoes_atuais}, relacoes_pos_normalizacao={relacoes_unicas}"
                    )
                )
                if not manter_secundarias:
                    self.stdout.write(
                        f"  dry-run: turmas_secundarias_a_remover={len(turmas_secundarias)}"
                    )
                continue

            with transaction.atomic():
                # Garante que os encontros de todos os dias fiquem vinculados a uma unica turma logica.
                for turma_origem in grupo_turmas:
                    _, criado = EncontroTurma.objects.get_or_create(
                        turma=turma_principal,
                        dia_semana=turma_origem.dia_semana,
                        horario_inicio=turma_origem.horario_inicio,
                        horario_fim=turma_origem.horario_fim,
                    )
                    if criado:
                        total_encontros_criados += 1

                relacoes_principal = set(
                    InscricaoTurma.objects.filter(turma=turma_principal).values_list("inscricao_id", flat=True)
                )

                for turma_secundaria in turmas_secundarias:
                    relacoes_sec = list(InscricaoTurma.objects.filter(turma=turma_secundaria))
                    for rel in relacoes_sec:
                        if rel.inscricao_id in relacoes_principal:
                            rel.delete()
                            total_relacoes_duplicadas_removidas += 1
                            continue

                        InscricaoTurma.objects.create(
                            inscricao_id=rel.inscricao_id,
                            turma=turma_principal,
                        )
                        relacoes_principal.add(rel.inscricao_id)
                        rel.delete()
                        total_relacoes_movidas += 1

                vagas_originais_grupo = max(t.vagas_originais for t in grupo_turmas)
                turma_principal.vagas_originais = vagas_originais_grupo
                inscritos_principal = InscricaoTurma.objects.filter(turma=turma_principal).count()
                turma_principal.vagas = max(0, vagas_originais_grupo - inscritos_principal)
                turma_principal.save(update_fields=["vagas_originais", "vagas"])

                if not manter_secundarias:
                    ids_secundarias = [t.id for t in turmas_secundarias]
                    total_turmas_secundarias_removidas += len(ids_secundarias)
                    Turma.objects.filter(id__in=ids_secundarias).delete()

        self.stdout.write("\nResumo:")
        self.stdout.write(f"- Grupos multi-dia processados: {total_grupos_processados}")
        self.stdout.write(f"- Encontros criados: {total_encontros_criados}")
        self.stdout.write(f"- Relacoes movidas para turma principal: {total_relacoes_movidas}")
        self.stdout.write(
            f"- Relacoes duplicadas removidas: {total_relacoes_duplicadas_removidas}"
        )
        self.stdout.write(
            f"- Turmas secundarias removidas: {total_turmas_secundarias_removidas}"
        )

        if confirmar:
            self.stdout.write(self.style.SUCCESS("Normalizacao concluida com sucesso."))
        else:
            self.stdout.write(self.style.SUCCESS("Dry-run concluido. Nenhum dado foi alterado."))
