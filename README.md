# Escola de Arte

**Descrição do Projeto**:  
Este é um projeto para gerenciar as inscrições e usuários de uma escola de arte. A aplicação permite que os usuários se inscrevam, façam login e interajam com o sistema de forma simples e intuitiva.

## Link do Projeto
Acesse o projeto em: [Escola de Arte](https://escola-arte.onrender.com/accounts/login/)

## Novas Funcionalidades e Melhorias

### Sistema de Horários
- Cadastro de horários específicos para cada curso
- Seleção de horário durante a inscrição
- Visualização de horários disponíveis por curso
- Controle de vagas por horário

### Interface Aprimorada
- Design moderno e responsivo
- Formulário de inscrição organizado em seções
- Máscara de telefone automática (formato: (11) 91111-1111)
- Feedback visual para ações do usuário
- Ícones intuitivos para melhor navegação

### Dashboard Administrativo
- Estatísticas em tempo real
- Gráficos interativos
- Tabela de inscrições com barra de rolagem
- Busca em tempo real nas inscrições
- Visualização detalhada dos dados

### Melhorias de Usabilidade
- Validação de formulários em tempo real
- Mensagens de feedback claras
- Navegação intuitiva
- Interface adaptativa para diferentes dispositivos

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
   - Preencha o formulário de inscrição com seus dados
   - Selecione o curso desejado
   - Escolha o horário disponível
   - Envie sua inscrição

4. **Painel Administrativo**:
   - Acesso exclusivo para administradores
   - Visualização de estatísticas e dados das inscrições
   - Gerenciamento de cursos, horários e usuários
   - Controle de vagas por horário

## Tecnologias Usadas

- **Django**: Framework web Python para desenvolvimento rápido
- **Bootstrap**: Framework CSS para design responsivo e moderno
- **PostgreSQL**: Banco de dados relacional para armazenamento dos dados
- **Render**: Plataforma de deploy e hospedagem
- **Git & GitHub**: Controle de versão e repositório de código
- **JavaScript**: Para interatividade e máscaras de formulário
- **Chart.js**: Para visualização de dados e gráficos

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
