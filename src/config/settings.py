"""
Configurações da aplicação WhatsApp Expense Tracker.
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    """Configurações base da aplicação."""
    
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key_change_in_production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # WhatsApp API
    WHATSAPP_API_URL = os.getenv('WHATSAPP_API_URL', 'https://graph.facebook.com/v21.0')
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    WHATSAPP_WEBHOOK_VERIFY_TOKEN = os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN')
    
    # Application
    APP_NAME = os.getenv('APP_NAME', 'WhatsApp Expense Tracker')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    
    # NLP
    SPACY_MODEL = 'pt_core_news_sm'
    
    # Categorias de gastos padrão
    DEFAULT_CATEGORIES = [
        'alimentação',
        'transporte',
        'combustível',
        'saúde',
        'educação',
        'lazer',
        'casa',
        'roupas',
        'outros'
    ]

class DevelopmentConfig(Config):
    """Configurações para ambiente de desenvolvimento."""
    DEBUG = True

class ProductionConfig(Config):
    """Configurações para ambiente de produção."""
    DEBUG = False
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("FLASK_SECRET_KEY deve ser definida em produção")

class TestingConfig(Config):
    """Configurações para testes."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuração baseada no ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

