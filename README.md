# Escola de Arte

**Descrição do Projeto**:  
Este é um projeto para gerenciar as inscrições e usuários de uma escola de arte. A aplicação permite que os usuários se inscrevam, façam login e interajam com o sistema de forma simples e intuitiva.

## Link do Projeto
Acesse o projeto em: [Escola de Arte](https://escola-arte.onrender.com/accounts/login/)

## Fluxo de Uso

1. **Criar Conta**:
   - Acesse o link do projeto
   - Clique em "Criar uma conta"
   - Preencha seus dados e crie sua conta

2. **Acesso ao Sistema**:
   - Faça login com suas credenciais
   - Você será redirecionado para a página inicial

3. **Inscrição em Cursos**:
   - Na página inicial, clique no botão "Inscrever-se"
   - Preencha o formulário de inscrição
   - Selecione os cursos desejados
   - Envie sua inscrição

4. **Painel Administrativo**:
   - Acesso exclusivo para administradores
   - Visualização de estatísticas e dados das inscrições
   - Gerenciamento de cursos e usuários

## Tecnologias Usadas

- **Django**: Framework web Python para desenvolvimento rápido
- **Bootstrap**: Framework CSS para design responsivo e moderno
- **PostgreSQL**: Banco de dados relacional para armazenamento dos dados
- **Render**: Plataforma de deploy e hospedagem
- **Git & GitHub**: Controle de versão e repositório de código

## Como Rodar o Projeto Localmente

### 1. **Clone o repositório**

```bash
git clone https://github.com/Megadurck/escola_arte.git
```

### 2. **Instale as dependências**

Com o ambiente virtual ativado, instale as dependências:

```bash
pip install -r requirements.txt
```

### 3. **Configure o banco de dados**

O projeto utiliza PostgreSQL. Configure as variáveis de ambiente com suas credenciais do banco de dados:

```bash
DATABASE_URL=postgresql://usuario:senha@host:porta/nome_do_banco
```

### 4. **Execute as migrações**

```bash
python manage.py migrate
```

### 5. **Crie um superusuário**

```bash
python manage.py createsuperuser
```

### 6. **Inicie o servidor**

```bash
python manage.py runserver
```

## Deploy

O projeto está hospedado na plataforma Render, que oferece:
- Deploy automático a cada push no repositório
- Banco de dados PostgreSQL gerenciado
- SSL automático
- Escalabilidade automática

## Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Faça commit das suas alterações
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
