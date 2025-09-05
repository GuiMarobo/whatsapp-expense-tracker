"""
Processador de mensagens para extrair informações de gastos.
"""
import re
import spacy
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from src.config.settings import Config

class MessageProcessor:
    """Processador de linguagem natural para mensagens de gastos."""
    
    def __init__(self):
        """Inicializa o processador com o modelo spaCy."""
        try:
            self.nlp = spacy.load(Config.SPACY_MODEL)
        except OSError:
            raise Exception(f"Modelo spaCy '{Config.SPACY_MODEL}' não encontrado. Execute: python -m spacy download {Config.SPACY_MODEL}")
        
        # Padrões para identificar valores monetários
        self.money_patterns = [
            r'(?:R\$\s*)?(\d+(?:[.,]\d{2})?)',  # R$ 50.00, R$50, 50.00, 50
            r'(\d+)\s*reais?',  # 50 reais
            r'(\d+)\s*(?:pila|pratas?)',  # 50 pila, 50 prata (gírias)
        ]
        
        # Palavras-chave para identificar gastos
        self.expense_keywords = [
            'gastei', 'gasto', 'paguei', 'comprei', 'saiu', 'custou',
            'despesa', 'débito', 'conta', 'fatura', 'pagamento'
        ]
        
        # Palavras-chave para relatórios
        self.report_keywords = [
            'relatório', 'relatorio', 'resumo', 'total', 'quanto gastei',
            'balanço', 'balanco', 'extrato', 'histórico', 'historico'
        ]
        
        # Mapeamento de categorias e suas variações
        self.category_mapping = {
            'alimentação': ['alimentação', 'alimentacao', 'comida', 'lanche', 'almoço', 'almoco', 
                          'jantar', 'café', 'cafe', 'restaurante', 'mercado', 'supermercado',
                          'padaria', 'açougue', 'acougue', 'feira', 'delivery'],
            'transporte': ['transporte', 'uber', 'taxi', 'ônibus', 'onibus', 'metro', 'metrô',
                         'trem', 'passagem', 'viagem', 'combustível', 'combustivel', 'gasolina',
                         'álcool', 'alcool', 'diesel', 'posto'],
            'combustível': ['combustível', 'combustivel', 'gasolina', 'álcool', 'alcool', 
                          'diesel', 'posto', 'abasteci', 'abastecer'],
            'saúde': ['saúde', 'saude', 'médico', 'medico', 'hospital', 'farmácia', 'farmacia',
                     'remédio', 'remedio', 'consulta', 'exame', 'dentista', 'plano de saúde'],
            'educação': ['educação', 'educacao', 'escola', 'faculdade', 'curso', 'livro',
                       'material escolar', 'mensalidade', 'matrícula', 'matricula'],
            'lazer': ['lazer', 'cinema', 'teatro', 'show', 'festa', 'bar', 'balada',
                     'entretenimento', 'diversão', 'diversao', 'jogo', 'streaming'],
            'casa': ['casa', 'aluguel', 'condomínio', 'condominio', 'luz', 'água', 'agua',
                    'gás', 'gas', 'internet', 'telefone', 'limpeza', 'móveis', 'moveis'],
            'roupas': ['roupas', 'roupa', 'calça', 'calca', 'camisa', 'sapato', 'tênis', 'tenis',
                      'vestido', 'saia', 'blusa', 'casaco', 'moda', 'shopping'],
            'outros': ['outros', 'diverso', 'vário', 'vario', 'geral']
        }
    
    def process_message(self, message: str) -> Dict:
        """
        Processa uma mensagem e extrai informações relevantes.
        
        Args:
            message (str): Mensagem do usuário
            
        Returns:
            Dict: Informações extraídas da mensagem
        """
        message = message.lower().strip()
        
        # Identifica o tipo de mensagem
        message_type = self._identify_message_type(message)
        
        result = {
            'type': message_type,
            'original_message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        if message_type == 'expense':
            expense_data = self._extract_expense_data(message)
            result.update(expense_data)
        elif message_type == 'report':
            report_data = self._extract_report_data(message)
            result.update(report_data)
        
        return result
    
    def _identify_message_type(self, message: str) -> str:
        """Identifica o tipo de mensagem (gasto, relatório, etc.)."""
        
        # Verifica se é uma solicitação de relatório
        for keyword in self.report_keywords:
            if keyword in message:
                return 'report'
        
        # Verifica se é um gasto
        for keyword in self.expense_keywords:
            if keyword in message:
                return 'expense'
        
        # Verifica se tem valor monetário (pode ser gasto implícito)
        if self._extract_amount(message):
            return 'expense'
        
        return 'unknown'
    
    def _extract_expense_data(self, message: str) -> Dict:
        """Extrai dados de gasto da mensagem."""
        
        amount = self._extract_amount(message)
        category = self._extract_category(message)
        description = self._extract_description(message)
        
        return {
            'amount': amount,
            'category': category,
            'description': description,
            'confidence': self._calculate_confidence(amount, category, description)
        }
    
    def _extract_report_data(self, message: str) -> Dict:
        """Extrai dados de solicitação de relatório."""
        
        category = self._extract_category(message)
        period = self._extract_period(message)
        
        return {
            'category': category,
            'period': period
        }
    
    def _extract_amount(self, message: str) -> Optional[float]:
        """Extrai valor monetário da mensagem."""
        
        for pattern in self.money_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                # Pega o primeiro valor encontrado
                amount_str = matches[0]
                # Normaliza o formato (substitui vírgula por ponto)
                amount_str = amount_str.replace(',', '.')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    def _extract_category(self, message: str) -> Optional[str]:
        """Extrai categoria do gasto da mensagem."""
        
        # Procura por palavras-chave de categorias
        for category, keywords in self.category_mapping.items():
            for keyword in keywords:
                if keyword in message:
                    return category
        
        # Se não encontrou categoria específica, usa NLP para tentar identificar
        doc = self.nlp(message)
        
        # Procura por substantivos que podem indicar categoria
        for token in doc:
            if token.pos_ == 'NOUN' and not token.is_stop:
                lemma = token.lemma_.lower()
                for category, keywords in self.category_mapping.items():
                    if lemma in keywords:
                        return category
        
        return 'outros'  # Categoria padrão
    
    def _extract_description(self, message: str) -> str:
        """Extrai descrição do gasto."""
        
        # Remove palavras-chave de gasto e valores monetários
        description = message
        
        # Remove palavras-chave de gasto
        for keyword in self.expense_keywords:
            description = re.sub(rf'\b{keyword}\b', '', description, flags=re.IGNORECASE)
        
        # Remove valores monetários
        for pattern in self.money_patterns:
            description = re.sub(pattern, '', description, flags=re.IGNORECASE)
        
        # Remove preposições comuns
        common_words = ['em', 'de', 'com', 'para', 'no', 'na', 'do', 'da', 'r$']
        for word in common_words:
            description = re.sub(rf'\b{word}\b', '', description, flags=re.IGNORECASE)
        
        # Limpa espaços extras
        description = ' '.join(description.split())
        
        return description.strip() or 'Gasto não especificado'
    
    def _extract_period(self, message: str) -> str:
        """Extrai período do relatório solicitado."""
        
        period_keywords = {
            'hoje': 'today',
            'ontem': 'yesterday',
            'semana': 'week',
            'mês': 'month',
            'mes': 'month',
            'ano': 'year',
            'total': 'all'
        }
        
        for keyword, period in period_keywords.items():
            if keyword in message:
                return period
        
        return 'month'  # Padrão: mês atual
    
    def _calculate_confidence(self, amount: Optional[float], category: Optional[str], 
                            description: str) -> float:
        """Calcula a confiança da extração de dados."""
        
        confidence = 0.0
        
        # Confiança baseada na presença de valor
        if amount is not None:
            confidence += 0.4
        
        # Confiança baseada na categoria
        if category and category != 'outros':
            confidence += 0.3
        elif category == 'outros':
            confidence += 0.1
        
        # Confiança baseada na descrição
        if description and description != 'Gasto não especificado':
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def get_categories(self) -> List[str]:
        """Retorna lista de categorias disponíveis."""
        return list(self.category_mapping.keys())
    
    def validate_message(self, message: str) -> Tuple[bool, str]:
        """
        Valida se a mensagem pode ser processada.
        
        Returns:
            Tuple[bool, str]: (é_válida, mensagem_de_erro)
        """
        if not message or not message.strip():
            return False, "Mensagem vazia"
        
        if len(message) > 500:
            return False, "Mensagem muito longa (máximo 500 caracteres)"
        
        return True, ""

