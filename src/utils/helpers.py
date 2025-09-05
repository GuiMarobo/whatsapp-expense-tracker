"""
Funções auxiliares para o projeto.
"""
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

def format_currency(amount: float) -> str:
    """
    Formata um valor monetário para exibição.
    
    Args:
        amount (float): Valor a ser formatado
        
    Returns:
        str: Valor formatado (ex: "R$ 50,00")
    """
    return f"R$ {amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def parse_currency(currency_str: str) -> Optional[float]:
    """
    Converte string de moeda para float.
    
    Args:
        currency_str (str): String com valor monetário
        
    Returns:
        Optional[float]: Valor convertido ou None se inválido
    """
    # Remove caracteres não numéricos exceto vírgula e ponto
    cleaned = re.sub(r'[^\d,.]', '', currency_str)
    
    if not cleaned:
        return None
    
    # Substitui vírgula por ponto para conversão
    cleaned = cleaned.replace(',', '.')
    
    try:
        return float(cleaned)
    except ValueError:
        return None

def format_date(date: datetime, format_type: str = 'short') -> str:
    """
    Formata uma data para exibição.
    
    Args:
        date (datetime): Data a ser formatada
        format_type (str): Tipo de formatação ('short', 'long', 'relative')
        
    Returns:
        str: Data formatada
    """
    if format_type == 'short':
        return date.strftime('%d/%m/%Y')
    elif format_type == 'long':
        return date.strftime('%d de %B de %Y')
    elif format_type == 'relative':
        now = datetime.now()
        diff = now - date
        
        if diff.days == 0:
            return 'Hoje'
        elif diff.days == 1:
            return 'Ontem'
        elif diff.days < 7:
            return f'{diff.days} dias atrás'
        elif diff.days < 30:
            weeks = diff.days // 7
            return f'{weeks} semana{"s" if weeks > 1 else ""} atrás'
        else:
            months = diff.days // 30
            return f'{months} mês{"es" if months > 1 else ""} atrás'
    
    return date.strftime('%d/%m/%Y')

def get_period_dates(period: str) -> tuple[datetime, datetime]:
    """
    Retorna as datas de início e fim para um período específico.
    
    Args:
        period (str): Período ('today', 'yesterday', 'week', 'month', 'year', 'all')
        
    Returns:
        tuple[datetime, datetime]: (data_inicio, data_fim)
    """
    now = datetime.now()
    
    if period == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'yesterday':
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'week':
        # Início da semana (segunda-feira)
        days_since_monday = now.weekday()
        start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == 'month':
        # Início do mês
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == 'year':
        # Início do ano
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    else:  # 'all' ou qualquer outro valor
        # Desde o início dos tempos até agora
        start = datetime(1900, 1, 1)
        end = now
    
    return start, end

def validate_phone_number(phone: str) -> bool:
    """
    Valida um número de telefone brasileiro.
    
    Args:
        phone (str): Número de telefone
        
    Returns:
        bool: True se válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cleaned = re.sub(r'\D', '', phone)
    
    # Verifica se tem 10 ou 11 dígitos (com DDD)
    if len(cleaned) not in [10, 11]:
        return False
    
    # Verifica se o DDD é válido (11-99)
    ddd = int(cleaned[:2])
    if ddd < 11 or ddd > 99:
        return False
    
    return True

def sanitize_input(text: str, max_length: int = 500) -> str:
    """
    Sanitiza entrada de texto do usuário.
    
    Args:
        text (str): Texto a ser sanitizado
        max_length (int): Comprimento máximo permitido
        
    Returns:
        str: Texto sanitizado
    """
    if not text:
        return ""
    
    # Remove caracteres de controle
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Limita o comprimento
    sanitized = sanitized[:max_length]
    
    # Remove espaços extras
    sanitized = ' '.join(sanitized.split())
    
    return sanitized.strip()

def generate_response_message(message_type: str, data: Dict[str, Any]) -> str:
    """
    Gera mensagem de resposta baseada no tipo e dados.
    
    Args:
        message_type (str): Tipo da mensagem ('expense_registered', 'report', 'error', etc.)
        data (Dict[str, Any]): Dados para construir a mensagem
        
    Returns:
        str: Mensagem formatada
    """
    if message_type == 'expense_registered':
        amount = format_currency(data.get('amount', 0))
        category = data.get('category', 'outros').title()
        return f"✅ Gasto de {amount} em {category} registrado com sucesso!"
    
    elif message_type == 'report':
        total = format_currency(data.get('total', 0))
        period = data.get('period', 'período')
        category = data.get('category', 'todas as categorias')
        
        if category != 'todas as categorias':
            category = category.title()
        
        return f"📊 Relatório {category}: Total de {total} no {period}."
    
    elif message_type == 'error':
        error_msg = data.get('message', 'Erro desconhecido')
        return f"❌ Erro: {error_msg}"
    
    elif message_type == 'help':
        return """
🤖 *WhatsApp Expense Tracker - Ajuda*

*Como registrar gastos:*
• "Gastei 50 reais em alimentação"
• "Combustível 120"
• "Paguei 30 no almoço"

*Como solicitar relatórios:*
• "Relatório alimentação"
• "Quanto gastei este mês"
• "Total de gastos"

*Categorias disponíveis:*
• Alimentação • Transporte • Combustível
• Saúde • Educação • Lazer
• Casa • Roupas • Outros

Digite "ajuda" a qualquer momento para ver esta mensagem.
        """.strip()
    
    elif message_type == 'unknown':
        return """
🤔 Não entendi sua mensagem. 

Tente algo como:
• "Gastei 50 reais em alimentação"
• "Relatório do mês"
• "ajuda" para ver todas as opções
        """.strip()
    
    return "Mensagem processada."

def get_emoji_for_category(category: str) -> str:
    """
    Retorna emoji apropriado para uma categoria.
    
    Args:
        category (str): Nome da categoria
        
    Returns:
        str: Emoji correspondente
    """
    emoji_map = {
        'alimentação': '🍽️',
        'transporte': '🚗',
        'combustível': '⛽',
        'saúde': '🏥',
        'educação': '📚',
        'lazer': '🎬',
        'casa': '🏠',
        'roupas': '👕',
        'outros': '📦'
    }
    
    return emoji_map.get(category.lower(), '📦')

