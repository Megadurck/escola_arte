# Escola de Arte

Aplicação web para inscrições em cursos da Escola de Artes, com foco em fluxo público simples:

- visitante acessa a página inicial
- escolhe cursos e horários
- envia inscrição sem cadastro/login público

O acesso autenticado ficou restrito ao painel administrativo.

## Estado atual do projeto

- Framework: Django 4.2
- Deploy: Render (web)
- Banco atual no código: PostgreSQL via DATABASE_URL
- Apps:
  - inscricoes: cursos, turmas, vagas, formulário e dashboard
  - accounts: legado de autenticação (não exposto no fluxo público)

## Fluxo de navegação

- / -> redireciona para /inscricoes/
- /inscricoes/ -> página inicial pública
- /inscricoes/inscrever/ -> formulário público (respeita INSCRICOES_ABERTAS)
- /admin/ -> painel administrativo (somente superuser)

## Controle de inscrições

Variável de ambiente:

- INSCRICOES_ABERTAS=True: formulário aberto
- INSCRICOES_ABERTAS=False: formulário retorna mensagem de inscrições encerradas

## Configuração local

1. Criar ambiente virtual

Windows:

python -m venv venv
venv\Scripts\activate

2. Instalar dependências

pip install -r requirements.txt

3. Configurar variáveis de ambiente no arquivo .env

Exemplo mínimo:

SECRET_KEY=sua_chave
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://usuario:senha@host:porta/banco
INSCRICOES_ABERTAS=False

4. Rodar migrações

python manage.py migrate

5. Criar superusuário

python manage.py createsuperuser

6. Executar o projeto

python manage.py runserver

## Deploy

Build command (Render):

./build.sh

Start command:

gunicorn escola_arte.wsgi:application

## Limpeza feita nesta etapa

- Removidas rotas públicas de login do fluxo principal
- Ajustados templates base para navegação pública objetiva
- Dashboard protegida via login admin
- README atualizado para o escopo real do sistema

## Próxima etapa (amanhã): migração para banco gratuito

Objetivo: reativar o site com menor custo possível.

Opções recomendadas:

- Neon (PostgreSQL free)
- Supabase (PostgreSQL free)

Plano resumido:

1. Criar banco gratuito
2. Restaurar backup válido:
   - backup_producao_20260420_1725.dump
3. Atualizar DATABASE_URL no serviço web
4. Validar formulário público e painel admin

## Observações de segurança

- Não versionar .env
- Rotacionar credenciais antigas (SECRET_KEY e senha de app de e-mail, se expostas)
- Em produção: DEBUG=False
