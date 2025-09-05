"""
Manipulador de mensagens do WhatsApp.
"""
import logging
from typing import Dict, Any, Optional
from src.nlp.message_processor import MessageProcessor
from src.services.expense_service import ExpenseService, CategoryService, UserSettingsService
from src.whatsapp.api_client import WhatsAppAPIClient
from src.utils.helpers import generate_response_message, format_currency, get_emoji_for_category

logger = logging.getLogger(__name__)

class MessageHandler:
    """Manipulador para processar mensagens do WhatsApp."""
    
    # Instâncias dos serviços
    _message_processor = None
    _whatsapp_client = None
    
    @classmethod
    def _get_message_processor(cls) -> MessageProcessor:
        """Retorna instância do processador de mensagens."""
        if cls._message_processor is None:
            cls._message_processor = MessageProcessor()
        return cls._message_processor
    
    @classmethod
    def _get_whatsapp_client(cls) -> WhatsAppAPIClient:
        """Retorna instância do cliente WhatsApp."""
        if cls._whatsapp_client is None:
            cls._whatsapp_client = WhatsAppAPIClient()
        return cls._whatsapp_client
    
    @classmethod
    def handle_incoming_message(cls, message: Dict[str, Any], 
                              value: Dict[str, Any]) -> Optional[str]:
        """
        Processa uma mensagem recebida do WhatsApp.
        
        Args:
            message (Dict): Dados da mensagem
            value (Dict): Dados do webhook
            
        Returns:
            Optional[str]: Resposta enviada ou None
        """
        try:
            # Extrai informações da mensagem
            message_id = message.get('id')
            from_number = message.get('from')
            message_type = message.get('type')
            timestamp = message.get('timestamp')
            
            logger.info(f"Processando mensagem {message_id} de {from_number}")
            
            # Marca a mensagem como lida
            cls._mark_as_read(message_id)
            
            # Processa diferentes tipos de mensagem
            if message_type == 'text':
                return cls._handle_text_message(message, from_number)
            elif message_type == 'interactive':
                return cls._handle_interactive_message(message, from_number)
            elif message_type in ['image', 'document', 'audio', 'video']:
                return cls._handle_media_message(message, from_number)
            else:
                logger.warning(f"Tipo de mensagem não suportado: {message_type}")
                return cls._send_unsupported_message_response(from_number)
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            return cls._send_error_response(from_number, str(e))
    
    @classmethod
    def _handle_text_message(cls, message: Dict[str, Any], 
                           from_number: str) -> Optional[str]:
        """Processa mensagem de texto."""
        
        text_body = message.get('text', {}).get('body', '').strip()
        
        if not text_body:
            return cls._send_error_response(from_number, "Mensagem vazia")
        
        logger.info(f"Texto recebido: {text_body}")
        
        # Verifica comandos especiais
        if text_body.lower() in ['ajuda', 'help', '/help', '/ajuda']:
            return cls._send_help_message(from_number)
        
        if text_body.lower() in ['estatisticas', 'stats', '/stats']:
            return cls._send_statistics(from_number)
        
        # Processa a mensagem com NLP
        processor = cls._get_message_processor()
        
        # Valida a mensagem
        is_valid, error_msg = processor.validate_message(text_body)
        if not is_valid:
            return cls._send_error_response(from_number, error_msg)
        
        # Processa a mensagem
        result = processor.process_message(text_body)
        
        if result['type'] == 'expense':
            return cls._handle_expense_message(result, from_number)
        elif result['type'] == 'report':
            return cls._handle_report_message(result, from_number)
        else:
            return cls._send_unknown_message_response(from_number)
    
    @classmethod
    def _handle_expense_message(cls, result: Dict[str, Any], 
                              from_number: str) -> Optional[str]:
        """Processa mensagem de gasto."""
        
        try:
            # Verifica se os dados são válidos
            amount = result.get('amount')
            if not amount or amount <= 0:
                return cls._send_error_response(
                    from_number, 
                    "Não consegui identificar o valor do gasto. Tente algo como 'Gastei 50 reais em alimentação'"
                )
            
            # Cria o gasto no banco de dados
            expense = ExpenseService.create_expense(from_number, result)
            
            # Gera mensagem de confirmação
            response_text = generate_response_message('expense_registered', {
                'amount': expense.amount,
                'category': expense.category
            })
            
            # Adiciona emoji da categoria
            emoji = get_emoji_for_category(expense.category)
            response_text = f"{emoji} {response_text}"
            
            # Se a confiança for baixa, adiciona aviso
            if result.get('confidence', 1.0) < 0.7:
                response_text += f"\n\n⚠️ Identifiquei automaticamente como '{expense.category}'. Se estiver errado, me avise!"
            
            return cls._send_text_message(from_number, response_text)
            
        except Exception as e:
            logger.error(f"Erro ao processar gasto: {str(e)}")
            return cls._send_error_response(from_number, "Erro ao registrar gasto")
    
    @classmethod
    def _handle_report_message(cls, result: Dict[str, Any], 
                             from_number: str) -> Optional[str]:
        """Processa mensagem de relatório."""
        
        try:
            category = result.get('category')
            period = result.get('period', 'month')
            
            # Obtém o total do período
            total = ExpenseService.get_total_by_period(from_number, period, category)
            
            # Gera mensagem de relatório
            period_names = {
                'today': 'hoje',
                'yesterday': 'ontem',
                'week': 'esta semana',
                'month': 'este mês',
                'year': 'este ano',
                'all': 'total geral'
            }
            
            period_name = period_names.get(period, period)
            
            if category and category != 'outros':
                category_name = category.title()
                emoji = get_emoji_for_category(category)
                response_text = f"{emoji} *Relatório {category_name}*\n"
            else:
                response_text = "📊 *Relatório Geral*\n"
            
            response_text += f"Período: {period_name}\n"
            response_text += f"Total gasto: {format_currency(total)}"
            
            # Se for relatório geral, adiciona resumo por categoria
            if not category or category == 'outros':
                summary = ExpenseService.get_category_summary(from_number, period)
                if summary:
                    response_text += "\n\n*Por categoria:*"
                    for item in summary[:5]:  # Máximo 5 categorias
                        emoji = get_emoji_for_category(item['category'])
                        response_text += f"\n{emoji} {item['category'].title()}: {format_currency(item['total'])}"
                    
                    if len(summary) > 5:
                        response_text += f"\n... e mais {len(summary) - 5} categorias"
            
            return cls._send_text_message(from_number, response_text)
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {str(e)}")
            return cls._send_error_response(from_number, "Erro ao gerar relatório")
    
    @classmethod
    def _handle_interactive_message(cls, message: Dict[str, Any], 
                                  from_number: str) -> Optional[str]:
        """Processa mensagem interativa (botões)."""
        
        interactive = message.get('interactive', {})
        button_reply = interactive.get('button_reply', {})
        button_id = button_reply.get('id')
        
        logger.info(f"Botão pressionado: {button_id}")
        
        # Processa diferentes botões
        if button_id == 'help':
            return cls._send_help_message(from_number)
        elif button_id == 'stats':
            return cls._send_statistics(from_number)
        else:
            return cls._send_text_message(from_number, "Opção não reconhecida.")
    
    @classmethod
    def _handle_media_message(cls, message: Dict[str, Any], 
                            from_number: str) -> Optional[str]:
        """Processa mensagem de mídia."""
        
        message_type = message.get('type')
        
        # Por enquanto, não processamos mídia, mas podemos expandir no futuro
        response_text = f"Recebi sua {message_type}, mas ainda não consigo processar arquivos. "
        response_text += "Por favor, envie o gasto como texto. Exemplo: 'Gastei 50 reais em alimentação'"
        
        return cls._send_text_message(from_number, response_text)
    
    @classmethod
    def _send_help_message(cls, from_number: str) -> Optional[str]:
        """Envia mensagem de ajuda."""
        
        help_text = generate_response_message('help', {})
        return cls._send_text_message(from_number, help_text)
    
    @classmethod
    def _send_statistics(cls, from_number: str) -> Optional[str]:
        """Envia estatísticas do usuário."""
        
        try:
            stats = ExpenseService.get_user_statistics(from_number)
            
            response_text = "📈 *Suas Estatísticas*\n\n"
            response_text += f"💰 Total gasto: {format_currency(stats['total_amount'])}\n"
            response_text += f"📝 Total de gastos: {stats['total_expenses']}\n\n"
            response_text += f"🗓️ Hoje: {format_currency(stats['today_total'])}\n"
            response_text += f"📅 Esta semana: {format_currency(stats['week_total'])}\n"
            response_text += f"📆 Este mês: {format_currency(stats['month_total'])}\n"
            
            if stats['most_used_category']:
                emoji = get_emoji_for_category(stats['most_used_category'])
                response_text += f"\n{emoji} Categoria mais usada: {stats['most_used_category'].title()}"
            
            return cls._send_text_message(from_number, response_text)
            
        except Exception as e:
            logger.error(f"Erro ao gerar estatísticas: {str(e)}")
            return cls._send_error_response(from_number, "Erro ao gerar estatísticas")
    
    @classmethod
    def _send_unknown_message_response(cls, from_number: str) -> Optional[str]:
        """Envia resposta para mensagem não reconhecida."""
        
        response_text = generate_response_message('unknown', {})
        return cls._send_text_message(from_number, response_text)
    
    @classmethod
    def _send_unsupported_message_response(cls, from_number: str) -> Optional[str]:
        """Envia resposta para tipo de mensagem não suportado."""
        
        response_text = "🤖 Ainda não consigo processar esse tipo de mensagem. "
        response_text += "Por favor, envie mensagens de texto com seus gastos."
        
        return cls._send_text_message(from_number, response_text)
    
    @classmethod
    def _send_error_response(cls, from_number: str, error_msg: str) -> Optional[str]:
        """Envia resposta de erro."""
        
        response_text = generate_response_message('error', {'message': error_msg})
        return cls._send_text_message(from_number, response_text)
    
    @classmethod
    def _send_text_message(cls, to: str, message: str) -> Optional[str]:
        """Envia mensagem de texto."""
        
        try:
            client = cls._get_whatsapp_client()
            
            if not client.is_configured():
                logger.warning("Cliente WhatsApp não configurado - simulando envio")
                logger.info(f"Mensagem para {to}: {message}")
                return message
            
            response = client.send_text_message(to, message)
            logger.info(f"Mensagem enviada com sucesso: {response}")
            return message
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {str(e)}")
            return None
    
    @classmethod
    def _mark_as_read(cls, message_id: str) -> None:
        """Marca mensagem como lida."""
        
        try:
            client = cls._get_whatsapp_client()
            
            if client.is_configured():
                client.mark_message_as_read(message_id)
                logger.info(f"Mensagem {message_id} marcada como lida")
            
        except Exception as e:
            logger.error(f"Erro ao marcar mensagem como lida: {str(e)}")
    
    @classmethod
    def handle_message_status(cls, status: Dict[str, Any]) -> None:
        """
        Processa status de mensagem (entregue, lida, etc.).
        
        Args:
            status (Dict): Dados do status da mensagem
        """
        message_id = status.get('id')
        status_type = status.get('status')
        
        logger.info(f"Status da mensagem {message_id}: {status_type}")
        
        # Aqui podemos implementar lógica para rastrear status das mensagens
        # Por exemplo, salvar no banco de dados ou enviar notificações

