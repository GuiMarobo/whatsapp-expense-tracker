"""
Modelo de dados para gastos.
"""
from datetime import datetime
from src.models.user import db

class Expense(db.Model):
    """Modelo para representar um gasto."""
    
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_phone = db.Column(db.String(20), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text)
    confidence = db.Column(db.Float, default=1.0)
    original_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Expense {self.id}: R${self.amount} - {self.category}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário."""
        return {
            'id': self.id,
            'user_phone': self.user_phone,
            'amount': self.amount,
            'category': self.category,
            'description': self.description,
            'confidence': self.confidence,
            'original_message': self.original_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create_from_message_data(cls, user_phone: str, message_data: dict):
        """
        Cria um novo gasto a partir dos dados processados da mensagem.
        
        Args:
            user_phone (str): Telefone do usuário
            message_data (dict): Dados processados da mensagem
            
        Returns:
            Expense: Nova instância de gasto
        """
        return cls(
            user_phone=user_phone,
            amount=message_data.get('amount', 0.0),
            category=message_data.get('category', 'outros'),
            description=message_data.get('description', ''),
            confidence=message_data.get('confidence', 1.0),
            original_message=message_data.get('original_message', '')
        )

class Category(db.Model):
    """Modelo para categorias de gastos."""
    
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    emoji = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'emoji': self.emoji,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserSettings(db.Model):
    """Modelo para configurações do usuário."""
    
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    default_category = db.Column(db.String(50), default='outros')
    currency_format = db.Column(db.String(10), default='BRL')
    timezone = db.Column(db.String(50), default='America/Sao_Paulo')
    notifications_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserSettings {self.user_phone}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário."""
        return {
            'id': self.id,
            'user_phone': self.user_phone,
            'default_category': self.default_category,
            'currency_format': self.currency_format,
            'timezone': self.timezone,
            'notifications_enabled': self.notifications_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

