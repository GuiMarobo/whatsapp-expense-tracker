# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2025-01-28

### Adicionado
- 🎉 **Lançamento inicial do WhatsApp Expense Tracker**
- 📱 **Integração completa com WhatsApp Business API**
  - Webhook para receber mensagens
  - Envio de respostas automáticas
  - Suporte a diferentes tipos de mensagem
  
- 🧠 **Processamento de Linguagem Natural**
  - Extração automática de valores monetários
  - Categorização inteligente de gastos
  - Suporte a múltiplos formatos de entrada
  - Modelo spaCy em português brasileiro
  
- 💾 **Sistema de Banco de Dados**
  - Modelos SQLAlchemy para gastos, categorias e configurações
  - Operações CRUD completas
  - Suporte a SQLite para desenvolvimento
  - Migrações automáticas
  
- 📊 **Relatórios e Análises**
  - Resumos por período (hoje, semana, mês, ano)
  - Análise por categoria
  - Gráficos de pizza e linha temporal
  - Exportação para CSV
  - Estatísticas personalizadas
  
- 🎯 **Categorias de Gastos**
  - 9 categorias pré-definidas
  - Mapeamento inteligente de palavras-chave
  - Emojis para melhor visualização
  - Sistema extensível para novas categorias
  
- 🔧 **API RESTful**
  - Endpoints para relatórios
  - Suporte a CORS
  - Documentação de endpoints
  - Health check
  
- 🧪 **Testes Automatizados**
  - Testes unitários para NLP
  - Testes de serviços
  - Cobertura de código
  - Testes de integração
  
- 📚 **Documentação Completa**
  - README detalhado
  - Guia de contribuição
  - Documentação de API
  - Exemplos de uso

### Funcionalidades Principais

#### 💬 Comandos Suportados
- **Registro de Gastos**: "Gastei 50 reais em alimentação"
- **Relatórios**: "Relatório alimentação", "Quanto gastei este mês"
- **Ajuda**: "ajuda", "help"
- **Estatísticas**: "estatisticas", "stats"

#### 🏷️ Categorias Disponíveis
- 🍽️ Alimentação
- 🚗 Transporte  
- ⛽ Combustível
- 🏥 Saúde
- 📚 Educação
- 🎬 Lazer
- 🏠 Casa
- 👕 Roupas
- 📦 Outros

#### 📈 Tipos de Relatório
- Resumo por período
- Gráfico de pizza por categoria
- Linha temporal de gastos
- Comparativo entre períodos
- Exportação CSV

### Tecnologias Utilizadas
- **Backend**: Flask, SQLAlchemy, Flask-CORS
- **NLP**: spaCy, regex patterns
- **Visualização**: Matplotlib, Seaborn, Pandas
- **API**: WhatsApp Business API, Requests
- **Testes**: pytest, unittest
- **Banco**: SQLite (desenvolvimento)

### Configuração
- Suporte a variáveis de ambiente
- Configuração flexível por ambiente
- Templates de configuração
- Documentação de setup

### Segurança
- Validação de entrada
- Sanitização de dados
- Verificação de webhook
- Tratamento de erros

---

## Formato das Versões

### [MAJOR.MINOR.PATCH] - YYYY-MM-DD

#### Adicionado
- Novas funcionalidades

#### Alterado  
- Mudanças em funcionalidades existentes

#### Descontinuado
- Funcionalidades que serão removidas

#### Removido
- Funcionalidades removidas

#### Corrigido
- Correções de bugs

#### Segurança
- Correções de vulnerabilidades

---

## Próximas Versões

### [1.1.0] - Planejado
- 🔄 **Sincronização em tempo real**
- 📱 **Interface web para visualização**
- 🔔 **Notificações automáticas**
- 📊 **Relatórios avançados**

### [1.2.0] - Planejado  
- 💳 **Integração com bancos**
- 🎯 **Metas de gastos**
- 👥 **Gastos compartilhados**
- 🌍 **Suporte a múltiplos idiomas**

### [2.0.0] - Futuro
- 🤖 **IA avançada para previsões**
- 📸 **Reconhecimento de recibos**
- 💰 **Controle de investimentos**
- 🏢 **Versão empresarial**

---

**Legenda:**
- 🎉 Lançamento
- ✨ Nova funcionalidade
- 🐛 Correção de bug
- 📚 Documentação
- 🔧 Melhoria técnica
- ⚡ Performance
- 🔒 Segurança

