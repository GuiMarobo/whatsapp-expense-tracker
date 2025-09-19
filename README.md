# WhatsApp Expense Tracker 💰📱

Um chatbot inteligente para controle de gastos pessoais via WhatsApp, desenvolvido em Python com Flask, SQLAlchemy e processamento de linguagem natural.

## 🚀 Funcionalidades

### 📝 Registro de Gastos
- **Processamento Natural**: Entende mensagens como "Gastei 50 reais em alimentação"
- **Categorização Automática**: Identifica automaticamente a categoria do gasto
- **Múltiplos Formatos**: Aceita diferentes formatos de entrada (R$ 50,00, 50 reais, etc.)
- **Confiança de Processamento**: Indica a confiança na interpretação da mensagem

### 📊 Relatórios e Análises
- **Relatórios por Período**: Hoje, semana, mês, ano ou período total
- **Análise por Categoria**: Breakdown detalhado dos gastos por categoria
- **Estatísticas Pessoais**: Totais, médias e categoria mais utilizada
- **Visualizações**: Gráficos de pizza, linha temporal e comparativos
- **Exportação**: Download de dados em formato CSV

### 🤖 Interface Inteligente
- **Comandos Naturais**: Comunicação em português brasileiro
- **Respostas Contextuais**: Feedback inteligente com emojis e formatação
- **Ajuda Integrada**: Sistema de ajuda acessível via comando
- **Validação de Entrada**: Verificação e sanitização de dados

## 🏗️ Arquitetura

### 📁 Estrutura do Projeto
```
whatsapp-expense-tracker/
├── src/
│   ├── config/          # Configurações da aplicação
│   ├── models/          # Modelos de dados (SQLAlchemy)
│   ├── services/        # Lógica de negócio
│   ├── nlp/            # Processamento de linguagem natural
│   ├── whatsapp/       # Integração com WhatsApp API
│   ├── reports/        # Geração de relatórios
│   ├── routes/         # Endpoints da API
│   ├── utils/          # Funções auxiliares
│   └── main.py         # Ponto de entrada da aplicação
├── tests/              # Testes unitários
├── requirements.txt    # Dependências Python
├── .env.example       # Exemplo de variáveis de ambiente
└── README.md          # Documentação
```

### 🔧 Tecnologias Utilizadas

#### Backend
- **Flask**: Framework web minimalista e flexível
- **SQLAlchemy**: ORM para gerenciamento de banco de dados
- **SQLite**: Banco de dados leve para desenvolvimento
- **Flask-CORS**: Suporte a requisições cross-origin

#### Processamento de Linguagem Natural
- **spaCy**: Biblioteca avançada de NLP
- **Modelo pt_core_news_sm**: Modelo em português brasileiro
- **Regex**: Padrões para extração de valores monetários

#### Análise de Dados e Visualização
- **Pandas**: Manipulação e análise de dados
- **Matplotlib**: Geração de gráficos e visualizações
- **Seaborn**: Visualizações estatísticas avançadas

#### Integração WhatsApp
- **WhatsApp Business API**: API oficial do Meta
- **Requests**: Cliente HTTP para comunicação com APIs
- **Webhook**: Recebimento de mensagens em tempo real

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.11+
- Conta WhatsApp Business
- Token de acesso da WhatsApp Business API

### 1. Clone o Repositório
```bash
git clone https://github.com/guimarobo/whatsapp-expense-tracker.git
cd whatsapp-expense-tracker
```

### 2. Configuração do Ambiente Virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instalação de Dependências
```bash
pip install -r requirements.txt
python -m spacy download pt_core_news_sm
```

### 4. Configuração de Variáveis de Ambiente
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:
```env
# WhatsApp API Configuration
WHATSAPP_API_URL=https://graph.facebook.com/v21.0
WHATSAPP_ACCESS_TOKEN=seu_token_aqui
WHATSAPP_PHONE_NUMBER_ID=seu_phone_id_aqui
WHATSAPP_WEBHOOK_VERIFY_TOKEN=seu_verify_token_aqui

# Flask Configuration
FLASK_SECRET_KEY=sua_chave_secreta_aqui
FLASK_ENV=development
FLASK_DEBUG=True
```

### 5. Inicialização do Banco de Dados
```bash
python src/main.py
```

O banco de dados SQLite será criado automaticamente com as tabelas necessárias.

## 🚀 Execução

### Desenvolvimento Local
```bash
python src/main.py
```

A aplicação estará disponível em `http://localhost:5000`

### Endpoints Principais
- `GET /health` - Health check da aplicação
- `POST /api/webhook` - Webhook para receber mensagens do WhatsApp
- `GET /api/webhook` - Verificação do webhook
- `POST /api/webhook/test` - Endpoint para testes locais

### Teste Local
```bash
python test_webhook.py
```

## 📱 Como Usar

### Registrar Gastos
Envie mensagens naturais para o WhatsApp:

```
Gastei 50 reais em alimentação
Combustível 120
Paguei 30 no almoço
Comprei roupas por R$ 85,50
Conta do médico deu 150 reais
```

### Solicitar Relatórios
```
Relatório alimentação
Quanto gastei este mês
Total de gastos
Resumo transporte
Balanço da semana
```

### Comandos Especiais
```
ajuda          # Exibe menu de ajuda
estatisticas   # Mostra estatísticas pessoais
```

## 🎯 Categorias Suportadas

- 🍽️ **Alimentação**: Comida, restaurantes, mercado
- 🚗 **Transporte**: Uber, taxi, ônibus, metro
- ⛽ **Combustível**: Gasolina, álcool, diesel
- 🏥 **Saúde**: Médico, farmácia, exames
- 📚 **Educação**: Escola, cursos, livros
- 🎬 **Lazer**: Cinema, shows, entretenimento
- 🏠 **Casa**: Aluguel, contas, móveis
- 👕 **Roupas**: Vestuário e acessórios
- 📦 **Outros**: Gastos diversos

## 🔧 Configuração do WhatsApp Business API

### 1. Criar Aplicação no Meta for Developers
1. Acesse [developers.facebook.com](https://developers.facebook.com)
2. Crie uma nova aplicação
3. Adicione o produto "WhatsApp Business API"

### 2. Configurar Webhook
1. Configure a URL do webhook: `https://seu-dominio.com/api/webhook`
2. Defina o token de verificação
3. Subscreva aos eventos de mensagens

### 3. Obter Credenciais
- **Access Token**: Token de acesso da aplicação
- **Phone Number ID**: ID do número de telefone
- **Verify Token**: Token para verificação do webhook

## 📊 API de Relatórios

### Endpoints Disponíveis

#### Resumo de Gastos
```http
GET /api/reports/summary/{user_phone}?period=month
```

#### Gráfico por Categoria
```http
GET /api/reports/chart/category/{user_phone}?period=month
```

#### Gráfico Timeline
```http
GET /api/reports/chart/timeline/{user_phone}?period=month
```

#### Exportar CSV
```http
GET /api/reports/export/csv/{user_phone}?period=month
```

### Períodos Suportados
- `today` - Hoje
- `yesterday` - Ontem  
- `week` - Esta semana
- `month` - Este mês
- `year` - Este ano
- `all` - Período total

## 🧪 Testes

### Executar Testes Unitários
```bash
python -m pytest tests/ -v
```

### Teste do Processamento NLP
```bash
python test_nlp.py
```

### Teste do Webhook
```bash
python test_webhook.py
```

## 🚀 Deploy

### Preparação para Produção
1. Configure variáveis de ambiente de produção
2. Use um banco de dados robusto (PostgreSQL)
3. Configure um servidor WSGI (Gunicorn)
4. Use HTTPS para o webhook

### Exemplo com Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

### Docker (Opcional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download pt_core_news_sm
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.main:app"]
```

## 🤝 Contribuição

### Como Contribuir
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Código
- Siga PEP 8 para Python
- Use docstrings para documentação
- Escreva testes para novas funcionalidades
- Mantenha cobertura de testes acima de 80%

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

### Problemas Comuns

#### Erro de Modelo spaCy
```bash
python -m spacy download pt_core_news_sm
```

#### Erro de Permissões do Webhook
Verifique se o token de verificação está correto no arquivo `.env`

#### Problemas de CORS
Certifique-se de que o Flask-CORS está instalado e configurado

### Contato
- 📧 Email: guimarobo@outlook.com
- 💬 Issues: [GitHub Issues](https://github.com/guimarobo/whatsapp-expense-tracker/issues)
- 📖 Wiki: [Documentação Completa](https://github.com/guimarobo/whatsapp-expense-tracker/wiki)


