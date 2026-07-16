from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

import csv

from inscricoes.models import Inscricao, InscricaoTurma, Turma


class Command(BaseCommand):
    help = (
        "Limpa inscrições de um ano letivo específico e restaura vagas das turmas desse ano. "
        "Mantém cursos e demais dados históricos de outros anos."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--ano",
            type=int,
            default=timezone.now().year - 1,
            help="Ano letivo alvo da limpeza. Padrão: ano anterior.",
        )
        parser.add_argument(
            "--confirmar",
            action="store_true",
            help="Confirma a execução. Sem esta flag, roda apenas em modo de pré-visualização.",
        )
        parser.add_argument(
            "--exportar-csv",
            type=str,
            help="Caminho de saída para exportar inscrições do ano alvo em CSV antes da limpeza.",
        )

    def handle(self, *args, **options):
        confirmar = options["confirmar"]
        ano = options["ano"]
        caminho_csv = options.get("exportar_csv")

        inscricoes_qs = Inscricao.objects.filter(ano_letivo=ano)
        turmas_qs = Turma.objects.filter(ano_letivo=ano)

        total_inscricoes = inscricoes_qs.count()
        total_relacoes = InscricaoTurma.objects.filter(inscricao__ano_letivo=ano).count()
        total_turmas = turmas_qs.count()

        self.stdout.write(f"Ano letivo alvo: {ano}")
        self.stdout.write("Resumo da operação de virada de ano:")
        self.stdout.write(f"- Inscrições do ano: {total_inscricoes}")
        self.stdout.write(f"- Relações inscrição/turma do ano: {total_relacoes}")
        self.stdout.write(f"- Turmas do ano a resetar vagas: {total_turmas}")

        if caminho_csv:
            self._exportar_csv(inscricoes_qs, caminho_csv)
            self.stdout.write(self.style.SUCCESS(f"Exportação concluída: {caminho_csv}"))

        if not confirmar:
            self.stdout.write(
                self.style.WARNING(
                    "Modo pré-visualização: nenhuma alteração foi aplicada. "
                    "Use --confirmar para executar de fato."
                )
            )
            return

        with transaction.atomic():
            # Remove inscrições apenas do ano letivo alvo (as relações na tabela intermediária
            # são removidas em cascata).
            inscricoes_qs.delete()

            # Garante que cada turma do ano alvo volte para sua capacidade original.
            for turma in turmas_qs.only("id", "vagas", "vagas_originais"):
                if turma.vagas != turma.vagas_originais:
                    turma.vagas = turma.vagas_originais
                    turma.save(update_fields=["vagas"])

        self.stdout.write(self.style.SUCCESS("Virada de ano concluída com sucesso."))
        self.stdout.write(self.style.SUCCESS(f"- Inscrições do ano {ano} foram removidas."))
        self.stdout.write(self.style.SUCCESS(f"- Vagas das turmas de {ano} foram restauradas."))

    def _exportar_csv(self, inscricoes_qs, caminho_csv):
        with open(caminho_csv, "w", newline="", encoding="utf-8") as arquivo:
            escritor = csv.writer(arquivo, delimiter=';')
            escritor.writerow([
                "id",
                "ano_letivo",
                "nome_completo",
                "cpf",
                "data_nascimento",
                "telefone_whatsapp",
                "rua",
                "bairro",
                "numero",
                "data_inscricao",
                "turmas",
            ])

            for inscricao in inscricoes_qs.prefetch_related("inscricaoturma_set__turma__curso"):
                turmas = [
                    f"{item.turma.curso.nome} - {item.turma.nome}"
                    for item in inscricao.inscricaoturma_set.all()
                ]

                escritor.writerow([
                    inscricao.id,
                    inscricao.ano_letivo,
                    inscricao.nome_completo,
                    inscricao.cpf,
                    inscricao.data_nascimento,
                    inscricao.telefone_whatsapp,
                    inscricao.rua,
                    inscricao.bairro,
                    inscricao.numero,
                    inscricao.data_inscricao,
                    " | ".join(turmas),
                ])
