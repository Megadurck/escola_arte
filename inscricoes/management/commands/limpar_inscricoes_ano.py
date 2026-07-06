from django.core.management.base import BaseCommand
from django.db import transaction

from inscricoes.models import Inscricao, InscricaoTurma, Turma


class Command(BaseCommand):
    help = (
        "Limpa todas as inscrições do ano anterior e restaura vagas das turmas. "
        "Mantém cursos, turmas e funcionários."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirmar",
            action="store_true",
            help="Confirma a execução. Sem esta flag, roda apenas em modo de pré-visualização.",
        )

    def handle(self, *args, **options):
        confirmar = options["confirmar"]

        total_inscricoes = Inscricao.objects.count()
        total_relacoes = InscricaoTurma.objects.count()
        total_turmas = Turma.objects.count()

        self.stdout.write("Resumo da operação de virada de ano:")
        self.stdout.write(f"- Inscrições atuais: {total_inscricoes}")
        self.stdout.write(f"- Relações inscrição/turma: {total_relacoes}")
        self.stdout.write(f"- Turmas a resetar vagas: {total_turmas}")

        if not confirmar:
            self.stdout.write(
                self.style.WARNING(
                    "Modo pré-visualização: nenhuma alteração foi aplicada. "
                    "Use --confirmar para executar de fato."
                )
            )
            return

        with transaction.atomic():
            # Remove todas as inscrições antigas (as relações na tabela intermediária
            # são removidas em cascata).
            Inscricao.objects.all().delete()

            # Garante que cada turma volte para sua capacidade original.
            for turma in Turma.objects.all().only("id", "vagas", "vagas_originais"):
                if turma.vagas != turma.vagas_originais:
                    turma.vagas = turma.vagas_originais
                    turma.save(update_fields=["vagas"])

        self.stdout.write(self.style.SUCCESS("Virada de ano concluída com sucesso."))
        self.stdout.write(self.style.SUCCESS("- Todas as inscrições foram removidas."))
        self.stdout.write(self.style.SUCCESS("- Vagas das turmas foram restauradas."))
