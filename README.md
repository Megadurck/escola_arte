# Escola de Arte

**Descrição do Projeto**:  
Este é um projeto para gerenciar as inscrições e usuários de uma escola de arte. A aplicação permite que os usuários se inscrevam, façam login e interajam com o sistema de forma simples e intuitiva. O sistema foi desenvolvido com foco na usabilidade e na experiência do usuário, oferecendo uma interface moderna e responsiva.

## Link do Projeto
Acesse o projeto em: [Escola de Arte](https://escola-arte.onrender.com/accounts/login/)

## Estrutura do Projeto

### Apps Django
- **accounts**: Gerenciamento de usuários e autenticação
- **inscricoes**: Core do sistema, gerencia inscrições, cursos e horários

### Principais Arquivos
- **settings.py**: Configurações do projeto
- **urls.py**: Roteamento das URLs
- **models.py**: Definição dos modelos de dados
- **views.py**: Lógica de negócio
- **forms.py**: Formulários do sistema
- **templates/**: Templates HTML
- **static/**: Arquivos estáticos (CSS, JS, imagens)

## Novas Funcionalidades e Melhorias

### Sistema de Horários
- Cadastro de horários específicos para cada curso
- Seleção de horário durante a inscrição
- Visualização de horários disponíveis por curso
- Controle de vagas por horário
- Sistema de validação para evitar conflitos de horários

### Interface Aprimorada
- Design moderno e responsivo
- Formulário de inscrição organizado em seções
- Máscara de telefone automática (formato: (11) 91111-1111)
- Feedback visual para ações do usuário
- Ícones intuitivos para melhor navegação
- Animações suaves para melhor experiência

### Dashboard Administrativo
- Estatísticas em tempo real
- Gráficos interativos
- Tabela de inscrições com barra de rolagem
- Busca em tempo real nas inscrições
- Visualização detalhada dos dados
- Exportação de dados em CSV
- Filtros avançados

### Melhorias de Usabilidade
- Validação de formulários em tempo real
- Mensagens de feedback claras
- Navegação intuitiva
- Interface adaptativa para diferentes dispositivos
- Suporte a temas claro/escuro
- Acessibilidade melhorada

## Fluxo de Uso

1. **Criar Conta**:
   - Acesse o link do projeto
   - Clique em "Criar uma conta"
   - Preencha seus dados e crie sua conta
   - Confirme seu email (opcional)

2. **Acesso ao Sistema**:
   - Faça login com suas credenciais
   - Você será redirecionado para a página inicial
   - Navegue pelo menu principal

3. **Inscrição em Cursos**:
   - Na página inicial, clique no botão "Inscrever-se"
   - Preencha o formulário de inscrição com seus dados
   - Selecione o curso desejado
   - Escolha o horário disponível
   - Revise suas escolhas
   - Envie sua inscrição

4. **Painel Administrativo**:
   - Acesso exclusivo para administradores
   - Visualização de estatísticas e dados das inscrições
   - Gerenciamento de cursos, horários e usuários
   - Controle de vagas por horário
   - Geração de relatórios

## Tecnologias Usadas

### Backend
- **Django 4.2**: Framework web Python para desenvolvimento rápido
- **PostgreSQL**: Banco de dados relacional para armazenamento dos dados
- **Django REST Framework**: Para construção da API (futuro)
- **Celery**: Para tarefas assíncronas (futuro)

### Frontend
- **Bootstrap 5**: Framework CSS para design responsivo e moderno
- **JavaScript**: Para interatividade e máscaras de formulário
- **Chart.js**: Para visualização de dados e gráficos
- **jQuery**: Para manipulação do DOM e AJAX
- **Font Awesome**: Para ícones

### DevOps
- **Git & GitHub**: Controle de versão e repositório de código
- **Render**: Plataforma de deploy e hospedagem
- **GitHub Actions**: Para CI/CD (futuro)

## Como Rodar o Projeto Localmente

### 1. **Preparação do Ambiente**
```bash
# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. **Clone o repositório**
```bash
git clone https://github.com/Megadurck/escola_arte.git
cd escola_arte
```

### 3. **Instale as dependências**
Com o ambiente virtual ativado, instale as dependências:
```bash
pip install -r requirements.txt
```

### 4. **Configure o banco de dados**
O projeto utiliza PostgreSQL. Configure as variáveis de ambiente com suas credenciais do banco de dados:
```bash
# Crie um arquivo .env na raiz do projeto
DATABASE_URL=postgresql://usuario:senha@host:porta/nome_do_banco
SECRET_KEY=sua_chave_secreta
DEBUG=True
```

### 5. **Execute as migrações**
```bash
python manage.py migrate
```

### 6. **Crie um superusuário**
```bash
python manage.py createsuperuser
```

### 7. **Colete arquivos estáticos**
```bash
python manage.py collectstatic
```

### 8. **Inicie o servidor**
```bash
python manage.py runserver
```

## Deploy

O projeto está hospedado na plataforma Render, que oferece:
- Deploy automático a cada push no repositório
- Banco de dados PostgreSQL gerenciado
- SSL automático
- Escalabilidade automática
- Monitoramento de recursos
- Logs em tempo real

### Processo de Deploy
1. Push para o repositório
2. Build automático no Render
3. Execução de migrações
4. Coleta de arquivos estáticos
5. Atualização do serviço

## Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Faça commit das suas alterações (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Diretrizes de Contribuição
- Siga o padrão de código existente
- Documente novas funcionalidades
- Adicione testes para novas features
- Atualize o README se necessário

## Roadmap

### Próximas Features
- [ ] Sistema de notificações por email
- [ ] API REST para integração com outros sistemas
- [ ] Área do aluno com progresso dos cursos
- [ ] Sistema de pagamentos
- [ ] App mobile

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contato

Romário - [@megadurck](https://github.com/Megadurck)

Link do Projeto: [https://github.com/Megadurck/escola_arte](https://github.com/Megadurck/escola_arte)
