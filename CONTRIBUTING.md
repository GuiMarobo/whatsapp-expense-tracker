# Guia de Contribuição 🤝

Obrigado por considerar contribuir para o WhatsApp Expense Tracker! Este documento fornece diretrizes para contribuições ao projeto.

## 🚀 Como Contribuir

### 1. Configuração do Ambiente de Desenvolvimento

#### Fork e Clone
```bash
# Fork o repositório no GitHub
git clone https://github.com/seu-usuario/whatsapp-expense-tracker.git
cd whatsapp-expense-tracker
```

#### Configuração Local
```bash
# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt
python -m spacy download pt_core_news_sm

# Instale dependências de desenvolvimento
pip install pytest pytest-cov black flake8 mypy
```

### 2. Fluxo de Desenvolvimento

#### Criando uma Branch
```bash
git checkout -b feature/nome-da-feature
# ou
git checkout -b bugfix/nome-do-bug
# ou
git checkout -b docs/melhoria-documentacao
```

#### Padrões de Nomenclatura
- `feature/` - Novas funcionalidades
- `bugfix/` - Correção de bugs
- `docs/` - Melhorias na documentação
- `refactor/` - Refatoração de código
- `test/` - Adição ou melhoria de testes

### 3. Padrões de Código

#### Python (PEP 8)
```python
# ✅ Bom
def process_expense_message(user_phone: str, message: str) -> Dict[str, Any]:
    """
    Processa mensagem de gasto do usuário.
    
    Args:
        user_phone: Telefone do usuário
        message: Mensagem recebida
        
    Returns:
        Dados processados da mensagem
    """
    # Implementação aqui
    pass

# ❌ Ruim
def processExpenseMessage(userPhone,message):
    # sem documentação
    pass
```

#### Formatação com Black
```bash
# Formatar código
black src/ tests/

# Verificar formatação
black --check src/ tests/
```

#### Linting com Flake8
```bash
# Verificar estilo de código
flake8 src/ tests/
```

#### Type Hints
```python
# ✅ Use type hints sempre que possível
from typing import Dict, List, Optional

def get_expenses(user_phone: str, limit: Optional[int] = None) -> List[Dict]:
    pass
```

### 4. Documentação

#### Docstrings
Use o formato Google para docstrings:

```python
def calculate_total(expenses: List[Expense], category: Optional[str] = None) -> float:
    """
    Calcula o total de gastos.
    
    Args:
        expenses: Lista de gastos
        category: Categoria específica (opcional)
        
    Returns:
        Total calculado
        
    Raises:
        ValueError: Se a lista de gastos estiver vazia
        
    Example:
        >>> expenses = [expense1, expense2]
        >>> total = calculate_total(expenses, 'alimentação')
        >>> print(total)
        150.0
    """
```

#### Comentários
```python
# ✅ Bom - explica o "porquê"
# Normaliza vírgula para ponto para conversão float
amount_str = amount_str.replace(',', '.')

# ❌ Ruim - explica o "o quê" (óbvio)
# Substitui vírgula por ponto
amount_str = amount_str.replace(',', '.')
```

### 5. Testes

#### Estrutura de Testes
```
tests/
├── __init__.py
├── test_nlp.py           # Testes do módulo NLP
├── test_services.py      # Testes dos serviços
├── test_whatsapp.py      # Testes da integração WhatsApp
├── test_reports.py       # Testes de relatórios
└── fixtures/             # Dados de teste
    ├── __init__.py
    └── sample_data.py
```

#### Escrevendo Testes
```python
import unittest
from unittest.mock import patch, MagicMock

class TestExpenseService(unittest.TestCase):
    """Testes para ExpenseService."""
    
    def setUp(self):
        """Configuração executada antes de cada teste."""
        self.service = ExpenseService()
        self.test_data = {
            'amount': 50.0,
            'category': 'alimentação',
            'description': 'Almoço'
        }
    
    def test_create_expense_success(self):
        """Testa criação bem-sucedida de gasto."""
        # Arrange
        user_phone = "5511999999999"
        
        # Act
        expense = self.service.create_expense(user_phone, self.test_data)
        
        # Assert
        self.assertIsNotNone(expense.id)
        self.assertEqual(expense.amount, 50.0)
        self.assertEqual(expense.category, 'alimentação')
    
    @patch('src.services.expense_service.db.session')
    def test_create_expense_database_error(self, mock_session):
        """Testa erro de banco de dados na criação."""
        # Arrange
        mock_session.commit.side_effect = Exception("Database error")
        
        # Act & Assert
        with self.assertRaises(Exception):
            self.service.create_expense("5511999999999", self.test_data)
```

#### Executando Testes
```bash
# Todos os testes
python -m pytest tests/ -v

# Testes específicos
python -m pytest tests/test_nlp.py -v

# Com cobertura
python -m pytest tests/ --cov=src --cov-report=html

# Testes rápidos (sem integração)
python -m pytest tests/ -m "not integration"
```

#### Cobertura de Testes
- Mantenha cobertura mínima de 80%
- Teste casos de sucesso e falha
- Inclua testes de edge cases
- Mock dependências externas

### 6. Commits e Pull Requests

#### Mensagens de Commit
Use o formato Conventional Commits:

```bash
# Formato
<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[rodapé opcional]
```

#### Exemplos
```bash
# Feature
feat(nlp): adiciona suporte para valores em centavos

# Bug fix
fix(webhook): corrige erro de timeout na API do WhatsApp

# Documentação
docs(readme): atualiza instruções de instalação

# Refatoração
refactor(services): simplifica lógica de cálculo de totais

# Testes
test(nlp): adiciona testes para extração de categorias
```

#### Pull Request
1. **Título claro**: Descreva o que foi alterado
2. **Descrição detalhada**: Explique o problema e a solução
3. **Checklist**: Use o template de PR
4. **Screenshots**: Para mudanças visuais
5. **Testes**: Certifique-se de que passam

#### Template de PR
```markdown
## Descrição
Breve descrição das mudanças realizadas.

## Tipo de Mudança
- [ ] Bug fix (mudança que corrige um problema)
- [ ] Nova feature (mudança que adiciona funcionalidade)
- [ ] Breaking change (mudança que quebra compatibilidade)
- [ ] Documentação

## Como Testar
1. Passos para reproduzir
2. Comportamento esperado
3. Comandos de teste

## Checklist
- [ ] Código segue os padrões do projeto
- [ ] Testes foram adicionados/atualizados
- [ ] Documentação foi atualizada
- [ ] Todos os testes passam
- [ ] Cobertura de testes mantida
```

### 7. Tipos de Contribuição

#### 🐛 Reportar Bugs
```markdown
**Descrição do Bug**
Descrição clara e concisa do problema.

**Reproduzir**
Passos para reproduzir o comportamento:
1. Vá para '...'
2. Clique em '....'
3. Role para baixo até '....'
4. Veja o erro

**Comportamento Esperado**
Descrição do que deveria acontecer.

**Screenshots**
Se aplicável, adicione screenshots.

**Ambiente:**
- OS: [ex: Ubuntu 20.04]
- Python: [ex: 3.11]
- Versão: [ex: 1.0.0]
```

#### ✨ Sugerir Features
```markdown
**Problema Relacionado**
Descrição clara do problema que a feature resolveria.

**Solução Proposta**
Descrição clara da solução desejada.

**Alternativas Consideradas**
Outras soluções que foram consideradas.

**Contexto Adicional**
Qualquer outro contexto sobre a feature.
```

#### 📚 Melhorar Documentação
- Corrigir erros de digitação
- Adicionar exemplos
- Melhorar clareza
- Traduzir conteúdo
- Adicionar diagramas

#### 🧪 Adicionar Testes
- Aumentar cobertura
- Testes de integração
- Testes de performance
- Testes de edge cases

### 8. Revisão de Código

#### Como Revisor
- **Seja construtivo**: Foque em melhorias, não críticas
- **Seja específico**: Aponte linhas e sugira soluções
- **Teste localmente**: Execute o código quando necessário
- **Verifique padrões**: Código, testes, documentação

#### Como Autor
- **Responda feedback**: Explique decisões quando necessário
- **Faça mudanças**: Implemente sugestões válidas
- **Seja paciente**: Revisão leva tempo
- **Aprenda**: Use feedback para melhorar

### 9. Configuração de Desenvolvimento

#### Hooks de Git
```bash
# Instalar pre-commit
pip install pre-commit

# Configurar hooks
pre-commit install
```

#### .pre-commit-config.yaml
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
```

#### VS Code Settings
```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "editor.formatOnSave": true
}
```

### 10. Recursos Úteis

#### Documentação
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [spaCy Documentation](https://spacy.io/usage)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)

#### Ferramentas
- [Black](https://black.readthedocs.io/) - Formatação de código
- [Flake8](https://flake8.pycqa.org/) - Linting
- [MyPy](https://mypy.readthedocs.io/) - Type checking
- [Pytest](https://docs.pytest.org/) - Framework de testes

### 11. Comunidade

#### Comunicação
- **Issues**: Para bugs e features
- **Discussions**: Para perguntas e ideias
- **Email**: Para questões privadas

#### Código de Conduta
- Seja respeitoso e inclusivo
- Aceite feedback construtivo
- Foque no que é melhor para a comunidade
- Mostre empatia com outros membros

---

**Obrigado por contribuir! 🎉**

Sua contribuição ajuda a tornar o controle de gastos mais acessível para todos.

