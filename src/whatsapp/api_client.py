"""
Cliente para interagir com a API do WhatsApp Business.
"""
import requests
import logging
from typing import Dict, Optional, Any
from src.config.settings import Config

logger = logging.getLogger(__name__)

class WhatsAppAPIClient:
    """Cliente para a API do WhatsApp Business."""
    
    def __init__(self):
        """Inicializa o cliente da API."""
        self.base_url = Config.WHATSAPP_API_URL
        self.access_token = Config.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = Config.WHATSAPP_PHONE_NUMBER_ID
        
        if not all([self.base_url, self.access_token, self.phone_number_id]):
            logger.warning("Configurações do WhatsApp não estão completas")
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna os headers para as requisições."""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Faz uma requisição para a API do WhatsApp.
        
        Args:
            method (str): Método HTTP (GET, POST, etc.)
            endpoint (str): Endpoint da API
            data (Dict, optional): Dados para enviar
            
        Returns:
            Dict: Resposta da API
        """
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=data)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para WhatsApp API: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Resposta da API: {e.response.text}")
            raise
    
    def send_text_message(self, to: str, message: str) -> Dict:
        """
        Envia uma mensagem de texto.
        
        Args:
            to (str): Número do destinatário
            message (str): Texto da mensagem
            
        Returns:
            Dict: Resposta da API
        """
        endpoint = f"{self.phone_number_id}/messages"
        
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        logger.info(f"Enviando mensagem para {to}: {message[:50]}...")
        return self._make_request('POST', endpoint, data)
    
    def send_template_message(self, to: str, template_name: str, 
                            language_code: str = 'pt_BR', 
                            parameters: Optional[list] = None) -> Dict:
        """
        Envia uma mensagem usando template.
        
        Args:
            to (str): Número do destinatário
            template_name (str): Nome do template
            language_code (str): Código do idioma
            parameters (list, optional): Parâmetros do template
            
        Returns:
            Dict: Resposta da API
        """
        endpoint = f"{self.phone_number_id}/messages"
        
        template_data = {
            "name": template_name,
            "language": {
                "code": language_code
            }
        }
        
        if parameters:
            template_data["components"] = [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": param} for param in parameters
                    ]
                }
            ]
        
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": template_data
        }
        
        logger.info(f"Enviando template {template_name} para {to}")
        return self._make_request('POST', endpoint, data)
    
    def send_interactive_message(self, to: str, header: str, body: str, 
                               buttons: list) -> Dict:
        """
        Envia uma mensagem interativa com botões.
        
        Args:
            to (str): Número do destinatário
            header (str): Cabeçalho da mensagem
            body (str): Corpo da mensagem
            buttons (list): Lista de botões
            
        Returns:
            Dict: Resposta da API
        """
        endpoint = f"{self.phone_number_id}/messages"
        
        interactive_buttons = []
        for i, button in enumerate(buttons[:3]):  # Máximo 3 botões
            interactive_buttons.append({
                "type": "reply",
                "reply": {
                    "id": f"button_{i}",
                    "title": button[:20]  # Máximo 20 caracteres
                }
            })
        
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "text",
                    "text": header
                },
                "body": {
                    "text": body
                },
                "action": {
                    "buttons": interactive_buttons
                }
            }
        }
        
        logger.info(f"Enviando mensagem interativa para {to}")
        return self._make_request('POST', endpoint, data)
    
    def mark_message_as_read(self, message_id: str) -> Dict:
        """
        Marca uma mensagem como lida.
        
        Args:
            message_id (str): ID da mensagem
            
        Returns:
            Dict: Resposta da API
        """
        endpoint = f"{self.phone_number_id}/messages"
        
        data = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        return self._make_request('POST', endpoint, data)
    
    def get_media(self, media_id: str) -> Dict:
        """
        Obtém informações sobre um arquivo de mídia.
        
        Args:
            media_id (str): ID do arquivo de mídia
            
        Returns:
            Dict: Informações do arquivo
        """
        endpoint = media_id
        return self._make_request('GET', endpoint)
    
    def download_media(self, media_url: str) -> bytes:
        """
        Baixa um arquivo de mídia.
        
        Args:
            media_url (str): URL do arquivo
            
        Returns:
            bytes: Conteúdo do arquivo
        """
        headers = self._get_headers()
        
        try:
            response = requests.get(media_url, headers=headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao baixar mídia: {str(e)}")
            raise
    
    def is_configured(self) -> bool:
        """
        Verifica se o cliente está configurado corretamente.
        
        Returns:
            bool: True se configurado, False caso contrário
        """
        return all([
            self.base_url,
            self.access_token,
            self.phone_number_id
        ])
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com a API do WhatsApp.
        
        Returns:
            bool: True se a conexão está funcionando
        """
        if not self.is_configured():
            logger.error("Cliente WhatsApp não está configurado")
            return False
        
        try:
            # Tenta obter informações do número de telefone
            endpoint = self.phone_number_id
            self._make_request('GET', endpoint)
            logger.info("Conexão com WhatsApp API testada com sucesso")
            return True
        except Exception as e:
            logger.error(f"Falha no teste de conexão: {str(e)}")
            return False

