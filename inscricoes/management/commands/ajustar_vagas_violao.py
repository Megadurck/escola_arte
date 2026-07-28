from django.core.management.base import BaseCommand
from django.db.models import Q

from inscricoes.models import Turma


class Command(BaseCommand):
    help = (
        "Ajusta vagas de turmas de Violao Adulto e Infantil. "
        "Por padrao define vagas e vagas_originais para 40."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--vagas",
            type=int,
            default=40,
            help="Numero de vagas para aplicar (padrao: 40).",
        )

    def handle(self, *args, **options):
        vagas_alvo = options["vagas"]

        if vagas_alvo < 0:
            self.stdout.write(self.style.ERROR("O valor de vagas nao pode ser negativo."))
            return

        turmas = Turma.objects.filter(
            curso__nome__icontains="viol",
        ).filter(
            Q(nome__icontains="adult")
            | Q(nome__icontains="aduldo")
            | Q(nome__icontains="infantil")
        )

        total = turmas.count()
        if total == 0:
            self.stdout.write(
                self.style.WARNING("Nenhuma turma de Violao Adulto/Infantil foi encontrada.")
            )
            return

        atualizadas = 0
        for turma in turmas.select_related("curso"):
            vagas_antes = turma.vagas
            vagas_originais_antes = turma.vagas_originais

            if vagas_antes == vagas_alvo and vagas_originais_antes == vagas_alvo:
                continue

            turma.vagas = vagas_alvo
            turma.vagas_originais = vagas_alvo
            turma.save(update_fields=["vagas", "vagas_originais"])
            atualizadas += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Turma {turma.id} - {turma.curso.nome} / {turma.nome}: "
                    f"vagas {vagas_antes} -> {vagas_alvo}, "
                    f"vagas_originais {vagas_originais_antes} -> {vagas_alvo}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Concluido. Turmas encontradas: {total}. Turmas atualizadas: {atualizadas}."
            )
        )
