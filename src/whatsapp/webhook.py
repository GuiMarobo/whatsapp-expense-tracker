"""
Webhook para receber mensagens do WhatsApp.
"""
import logging
from flask import Blueprint, request, jsonify
from src.config.settings import Config
from src.whatsapp.message_handler import MessageHandler

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint para o webhook
webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Verifica o webhook do WhatsApp.
    
    O WhatsApp envia uma requisição GET para verificar se o webhook é válido.
    """
    # Parâmetros enviados pelo WhatsApp
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    logger.info(f"Verificação do webhook: mode={mode}, token={token}")
    
    # Verifica se o token é válido
    if mode == 'subscribe' and token == Config.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
        logger.info("Webhook verificado com sucesso")
        return challenge, 200
    else:
        logger.warning("Falha na verificação do webhook")
        return 'Forbidden', 403

@webhook_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    Processa mensagens recebidas do WhatsApp.
    
    O WhatsApp envia uma requisição POST com os dados da mensagem.
    """
    try:
        # Obtém os dados da requisição
        data = request.get_json()
        
        if not data:
            logger.warning("Dados vazios recebidos no webhook")
            return jsonify({'status': 'error', 'message': 'No data received'}), 400
        
        logger.info(f"Dados recebidos: {data}")
        
        # Verifica se há entradas na mensagem
        if 'entry' not in data:
            logger.warning("Formato de dados inválido - sem 'entry'")
            return jsonify({'status': 'ok'}), 200
        
        # Processa cada entrada
        for entry in data['entry']:
            if 'changes' not in entry:
                continue
                
            for change in entry['changes']:
                if change.get('field') != 'messages':
                    continue
                
                value = change.get('value', {})
                
                # Processa mensagens recebidas
                if 'messages' in value:
                    for message in value['messages']:
                        MessageHandler.handle_incoming_message(message, value)
                
                # Processa status de mensagens (entregue, lida, etc.)
                if 'statuses' in value:
                    for status in value['statuses']:
                        MessageHandler.handle_message_status(status)
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@webhook_bp.route('/webhook/test', methods=['POST'])
def test_webhook():
    """
    Endpoint para testar o processamento de mensagens localmente.
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data or 'phone' not in data:
            return jsonify({
                'status': 'error', 
                'message': 'Formato inválido. Use: {"message": "texto", "phone": "5511999999999"}'
            }), 400
        
        # Simula uma mensagem do WhatsApp
        fake_message = {
            'id': 'test_message_id',
            'from': data['phone'],
            'timestamp': '1234567890',
            'text': {'body': data['message']},
            'type': 'text'
        }
        
        fake_value = {
            'messaging_product': 'whatsapp',
            'metadata': {
                'display_phone_number': '15550123456',
                'phone_number_id': Config.WHATSAPP_PHONE_NUMBER_ID
            }
        }
        
        # Processa a mensagem
        response = MessageHandler.handle_incoming_message(fake_message, fake_value)
        
        return jsonify({
            'status': 'ok',
            'message': 'Mensagem processada com sucesso',
            'response': response
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no teste do webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

