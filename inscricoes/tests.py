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
    def test_usuario_autenticado_com_inscricao_ainda_acessa_formulario_publico(self):
        self.client.login(username="usuario_teste", password="senha-forte-123")
        response = self.client.get(reverse("inscricoes:inscrever"))
        self.assertEqual(response.status_code, 200)


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
        inscricao_existente = Inscricao.objects.create(
            nome_completo="Aluno atual",
            cpf="99999999999",
            ano_letivo=2026,
            data_nascimento=date(1994, 1, 1),
            telefone_whatsapp="11922222222",
            rua="Rua B",
            bairro="Bairro B",
            numero="200",
        )
        InscricaoTurma.objects.create(inscricao=inscricao_existente, turma=self.turma_2026)

        response = self.client.post(reverse("inscricoes:inscrever"), self._dados_validos("99999999999"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Inscricao.objects.filter(cpf="99999999999", ano_letivo=2026).count(),
            1,
        )

    def test_reenvio_do_mesmo_formulario_nao_cria_duas_inscricoes(self):
        dados = self._dados_validos("22233344455")

        primeira_resposta = self.client.post(reverse("inscricoes:inscrever"), dados)
        self.assertEqual(primeira_resposta.status_code, 302)

        segunda_resposta = self.client.post(reverse("inscricoes:inscrever"), dados)
        self.assertEqual(segunda_resposta.status_code, 200)
        self.assertEqual(
            Inscricao.objects.filter(cpf="22233344455", ano_letivo=2026).count(),
            1,
        )

    def test_cpf_mascarado_tambem_e_bloqueado_quando_duplicado(self):
        inscricao_existente = Inscricao.objects.create(
            nome_completo="Aluno com CPF numerico",
            cpf="12345678901",
            ano_letivo=2026,
            data_nascimento=date(1990, 1, 1),
            telefone_whatsapp="11933334444",
            rua="Rua C",
            bairro="Bairro C",
            numero="300",
        )
        InscricaoTurma.objects.create(inscricao=inscricao_existente, turma=self.turma_2026)

        response = self.client.post(reverse("inscricoes:inscrever"), self._dados_validos("123.456.789-01"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Inscricao.objects.filter(cpf="12345678901", ano_letivo=2026).count(),
            1,
        )

    def test_post_com_turma_sem_cursos_explicitos_ainda_salva(self):
        dados = self._dados_validos("55566677788")
        dados.pop("cursos")

        response = self.client.post(reverse("inscricoes:inscrever"), dados)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Inscricao.objects.filter(cpf="55566677788", ano_letivo=2026).exists())

    def test_post_com_checkbox_turmas_sem_campo_oculto_ainda_salva(self):
        dados = self._dados_validos("44455566677")
        dados.pop("turmas_selecionadas")

        response = self.client.post(reverse("inscricoes:inscrever"), dados)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Inscricao.objects.filter(cpf="44455566677", ano_letivo=2026).exists())

    def test_cpf_com_mascara_e_espacos_e_normalizado_antes_da_validacao(self):
        dados = self._dados_validos("11122233344")
        dados["cpf"] = " 111.222.333-44  "

        response = self.client.post(reverse("inscricoes:inscrever"), dados)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Inscricao.objects.filter(cpf="11122233344", ano_letivo=2026).exists())

    def test_cpf_com_inscricao_incompleta_e_reaproveitado(self):
        inscricao_incompleta = Inscricao.objects.create(
            nome_completo="Cadastro incompleto",
            cpf="77766655544",
            ano_letivo=2026,
            data_nascimento=date(1991, 1, 1),
            telefone_whatsapp="11988887777",
            rua="Rua Antiga",
            bairro="Bairro Antigo",
            numero="999",
        )

        dados = self._dados_validos("77766655544")
        dados["nome_completo"] = "Aluno Recuperado"
        response = self.client.post(reverse("inscricoes:inscrever"), dados)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Inscricao.objects.filter(cpf="77766655544", ano_letivo=2026).count(), 1)

        inscricao_atualizada = Inscricao.objects.get(pk=inscricao_incompleta.pk)
        self.assertEqual(inscricao_atualizada.nome_completo, "Aluno Recuperado")
        self.assertEqual(inscricao_atualizada.turmas.count(), 1)
        self.assertEqual(inscricao_atualizada.turmas.first().id, self.turma_2026.id)

    def test_cpf_invalido_retorna_erro_de_tamanho_e_nao_duplicidade(self):
        Inscricao.objects.create(
            nome_completo="Aluno existente",
            cpf="12345678901",
            ano_letivo=2026,
            data_nascimento=date(1992, 2, 2),
            telefone_whatsapp="11911112222",
            rua="Rua X",
            bairro="Bairro X",
            numero="1",
        )

        dados = self._dados_validos("123")
        response = self.client.post(reverse("inscricoes:inscrever"), dados)

        self.assertEqual(response.status_code, 200)
        mensagens = [str(msg) for msg in response.context["messages"]]
        self.assertTrue(any("CPF deve conter 11 dígitos." in mensagem for mensagem in mensagens))
        self.assertFalse(any("já cadastrado" in mensagem for mensagem in mensagens))
