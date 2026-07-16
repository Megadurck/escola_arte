from datetime import date, time

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Curso, Inscricao, InscricaoTurma, Turma


@override_settings(ALLOWED_HOSTS=["testserver", "localhost"], INSCRICOES_ABERTAS=False)
class FluxoPublicoInscricoesTests(TestCase):
    def setUp(self):
        self.curso = Curso.objects.create(
            nome="Capoeira",
            descricao="Curso teste",
            valor=0,
            vagas_total=30,
        )
        self.turma = Turma.objects.create(
            curso=self.curso,
            nome="Turma A",
            dia_semana="Segunda-feira",
            horario_inicio=time(19, 0),
            horario_fim=time(21, 0),
            vagas=2,
        )

    def test_raiz_redireciona_para_fluxo_publico(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/inscricoes/")

    def test_pagina_inicial_publica(self):
        response = self.client.get(reverse("inscricoes:pagina_inicial"))
        self.assertEqual(response.status_code, 200)

    def test_get_turmas_publico_retorna_json(self):
        response = self.client.get(reverse("inscricoes:get_turmas"), {"curso_id": self.curso.id})
        self.assertEqual(response.status_code, 200)
        self.assertIn("turmas", response.json())

    @override_settings(INSCRICOES_ABERTAS=True)
    def test_inscricao_anonima_acessa_formulario_quando_aberto(self):
        response = self.client.get(reverse("inscricoes:inscrever"))
        self.assertEqual(response.status_code, 200)

    def test_inscricao_fechada_retorna_403(self):
        response = self.client.get(reverse("inscricoes:inscrever"))
        self.assertEqual(response.status_code, 403)

    def test_pagina_inicial_sem_link_de_login_publico(self):
        response = self.client.get(reverse("inscricoes:pagina_inicial"))
        self.assertNotContains(response, "/accounts/login/")

    @override_settings(INSCRICOES_ABERTAS=True)
    def test_pagina_inicial_exibe_botao_inscrever_quando_aberto(self):
        response = self.client.get(reverse("inscricoes:pagina_inicial"))
        self.assertContains(response, "Inscreva-se")

    def test_pagina_inicial_exibe_inscricoes_encerradas_quando_fechado(self):
        response = self.client.get(reverse("inscricoes:pagina_inicial"))
        self.assertContains(response, "Inscri\u00e7\u00f5es Encerradas")


@override_settings(ALLOWED_HOSTS=["testserver", "localhost"])
class SegurancaAdminTests(TestCase):
    def test_admin_exige_autenticacao(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_dashboard_exige_login(self):
        response = self.client.get(reverse("inscricoes:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)


@override_settings(ALLOWED_HOSTS=["testserver", "localhost"], INSCRICOES_ABERTAS=False)
class RegrasDeInscricaoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="usuario_teste", password="senha-forte-123")
        self.curso = Curso.objects.create(
            nome="Teatro",
            descricao="Curso teste",
            valor=0,
            vagas_total=30,
        )
        self.turma = Turma.objects.create(
            curso=self.curso,
            nome="Turma B",
            dia_semana="Terca-feira",
            horario_inicio=time(17, 0),
            horario_fim=time(19, 0),
            vagas=10,
        )
        self.inscricao = Inscricao.objects.create(
            usuario=self.user,
            nome_completo="Usuario Cadastrado",
            cpf="99988877766",
            data_nascimento=date(1990, 5, 20),
            telefone_whatsapp="89999998888",
            rua="Rua B",
            bairro="Bairro B",
            numero="200",
        )
        InscricaoTurma.objects.create(inscricao=self.inscricao, turma=self.turma)

    @override_settings(INSCRICOES_ABERTAS=True)
    def test_usuario_autenticado_com_inscricao_e_redirecionado(self):
        self.client.login(username="usuario_teste", password="senha-forte-123")
        response = self.client.get(reverse("inscricoes:inscrever"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("inscricoes:pagina_inicial"))


@override_settings(ALLOWED_HOSTS=["testserver", "localhost"], INSCRICOES_ABERTAS=True, ANO_LETIVO_ATUAL=2026)
class AnoLetivoInscricaoTests(TestCase):
    def setUp(self):
        self.curso = Curso.objects.create(
            nome="Danca",
            descricao="Curso teste",
            valor=0,
            vagas_total=30,
        )
        self.turma_2026 = Turma.objects.create(
            curso=self.curso,
            nome="Turma 2026",
            ano_letivo=2026,
            dia_semana="Quarta-feira",
            horario_inicio=time(18, 0),
            horario_fim=time(20, 0),
            vagas=5,
        )
        Turma.objects.create(
            curso=self.curso,
            nome="Turma 2025",
            ano_letivo=2025,
            dia_semana="Quarta-feira",
            horario_inicio=time(14, 0),
            horario_fim=time(16, 0),
            vagas=5,
        )

    def _dados_validos(self, cpf):
        return {
            "nome_completo": "Teste Aluno",
            "cpf": cpf,
            "data_nascimento": "1999-02-10",
            "telefone_whatsapp": "11999999999",
            "rua": "Rua 1",
            "bairro": "Centro",
            "numero": "10",
            "cursos": [str(self.curso.id)],
            "turmas": [str(self.turma_2026.id)],
            "turmas_selecionadas": str(self.turma_2026.id),
        }

    def test_get_turmas_retorna_apenas_ano_letivo_atual(self):
        response = self.client.get(reverse("inscricoes:get_turmas"), {"curso_id": self.curso.id})
        self.assertEqual(response.status_code, 200)
        turmas = response.json()["turmas"]
        self.assertEqual(len(turmas), 1)
        self.assertEqual(turmas[0]["id"], self.turma_2026.id)

    def test_cpf_pode_repetir_em_anos_diferentes(self):
        Inscricao.objects.create(
            nome_completo="Aluno antigo",
            cpf="12345678901",
            ano_letivo=2025,
            data_nascimento=date(1995, 1, 1),
            telefone_whatsapp="11911111111",
            rua="Rua A",
            bairro="Bairro A",
            numero="100",
        )

        response = self.client.post(reverse("inscricoes:inscrever"), self._dados_validos("12345678901"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Inscricao.objects.filter(cpf="12345678901", ano_letivo=2026).exists()
        )

    def test_cpf_duplicado_no_mesmo_ano_e_bloqueado(self):
        Inscricao.objects.create(
            nome_completo="Aluno atual",
            cpf="99999999999",
            ano_letivo=2026,
            data_nascimento=date(1994, 1, 1),
            telefone_whatsapp="11922222222",
            rua="Rua B",
            bairro="Bairro B",
            numero="200",
        )

        response = self.client.post(reverse("inscricoes:inscrever"), self._dados_validos("99999999999"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Inscricao.objects.filter(cpf="99999999999", ano_letivo=2026).count(),
            1,
        )
