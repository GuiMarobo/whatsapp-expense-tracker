"""
Testes para os serviços da aplicação.
"""
import unittest
import sys
import os
from datetime import datetime

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from src.services.expense_service import ExpenseService, CategoryService
from src.models.user import db
from src.models.expense import Expense, Category
from flask import Flask

class TestExpenseService(unittest.TestCase):
    """Testes para ExpenseService."""
    
    def setUp(self):
        """Configura o teste com banco em memória."""
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True
        
        db.init_app(self.app)
        
        with self.app.app_context():
            db.create_all()
            CategoryService.initialize_default_categories()
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        self.test_phone = "5511999999999"
    
    def tearDown(self):
        """Limpa após o teste."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_expense(self):
        """Testa criação de gasto."""
        message_data = {
            'amount': 50.0,
            'category': 'alimentação',
            'description': 'Almoço',
            'confidence': 1.0,
            'original_message': 'Gastei 50 reais em alimentação'
        }
        
        expense = ExpenseService.create_expense(self.test_phone, message_data)
        
        self.assertIsNotNone(expense.id)
        self.assertEqual(expense.user_phone, self.test_phone)
        self.assertEqual(expense.amount, 50.0)
        self.assertEqual(expense.category, 'alimentação')
        self.assertEqual(expense.description, 'Almoço')
    
    def test_get_expenses_by_user(self):
        """Testa busca de gastos por usuário."""
        # Cria alguns gastos
        for i in range(3):
            message_data = {
                'amount': 10.0 * (i + 1),
                'category': 'alimentação',
                'description': f'Gasto {i + 1}',
                'confidence': 1.0,
                'original_message': f'Gasto {i + 1}'
            }
            ExpenseService.create_expense(self.test_phone, message_data)
        
        expenses = ExpenseService.get_expenses_by_user(self.test_phone)
        
        self.assertEqual(len(expenses), 3)
        # Verifica se estão ordenados por data (mais recente primeiro)
        self.assertGreaterEqual(expenses[0].created_at, expenses[1].created_at)
    
    def test_get_total_by_period(self):
        """Testa cálculo de total por período."""
        # Cria gastos
        message_data1 = {
            'amount': 30.0,
            'category': 'alimentação',
            'description': 'Gasto 1',
            'confidence': 1.0,
            'original_message': 'Gasto 1'
        }
        message_data2 = {
            'amount': 20.0,
            'category': 'transporte',
            'description': 'Gasto 2',
            'confidence': 1.0,
            'original_message': 'Gasto 2'
        }
        
        ExpenseService.create_expense(self.test_phone, message_data1)
        ExpenseService.create_expense(self.test_phone, message_data2)
        
        total = ExpenseService.get_total_by_period(self.test_phone, 'all')
        self.assertEqual(total, 50.0)
        
        # Testa filtro por categoria
        total_food = ExpenseService.get_total_by_period(self.test_phone, 'all', 'alimentação')
        self.assertEqual(total_food, 30.0)
    
    def test_get_category_summary(self):
        """Testa resumo por categoria."""
        # Cria gastos em diferentes categorias
        categories_data = [
            ('alimentação', 50.0),
            ('alimentação', 30.0),
            ('transporte', 20.0)
        ]
        
        for category, amount in categories_data:
            message_data = {
                'amount': amount,
                'category': category,
                'description': 'Teste',
                'confidence': 1.0,
                'original_message': 'Teste'
            }
            ExpenseService.create_expense(self.test_phone, message_data)
        
        summary = ExpenseService.get_category_summary(self.test_phone, 'all')
        
        # Verifica se há 2 categorias
        self.assertEqual(len(summary), 2)
        
        # Verifica totais
        food_summary = next(item for item in summary if item['category'] == 'alimentação')
        self.assertEqual(food_summary['total'], 80.0)
        self.assertEqual(food_summary['count'], 2)
        
        transport_summary = next(item for item in summary if item['category'] == 'transporte')
        self.assertEqual(transport_summary['total'], 20.0)
        self.assertEqual(transport_summary['count'], 1)
    
    def test_get_user_statistics(self):
        """Testa estatísticas do usuário."""
        # Cria alguns gastos
        message_data = {
            'amount': 100.0,
            'category': 'alimentação',
            'description': 'Teste',
            'confidence': 1.0,
            'original_message': 'Teste'
        }
        ExpenseService.create_expense(self.test_phone, message_data)
        
        stats = ExpenseService.get_user_statistics(self.test_phone)
        
        self.assertEqual(stats['total_expenses'], 1)
        self.assertEqual(stats['total_amount'], 100.0)
        self.assertEqual(stats['most_used_category'], 'alimentação')

class TestCategoryService(unittest.TestCase):
    """Testes para CategoryService."""
    
    def setUp(self):
        """Configura o teste."""
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True
        
        db.init_app(self.app)
        
        with self.app.app_context():
            db.create_all()
        
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Limpa após o teste."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_category(self):
        """Testa criação de categoria."""
        category = CategoryService.create_category(
            name="teste",
            description="Categoria de teste",
            emoji="🧪"
        )
        
        self.assertIsNotNone(category.id)
        self.assertEqual(category.name, "teste")
        self.assertEqual(category.description, "Categoria de teste")
        self.assertEqual(category.emoji, "🧪")
        self.assertTrue(category.is_active)
    
    def test_initialize_default_categories(self):
        """Testa inicialização de categorias padrão."""
        CategoryService.initialize_default_categories()
        
        categories = CategoryService.get_all_categories()
        category_names = [cat.name for cat in categories]
        
        # Verifica se as categorias padrão foram criadas
        expected_categories = [
            'alimentação', 'transporte', 'combustível', 'saúde',
            'educação', 'lazer', 'casa', 'roupas', 'outros'
        ]
        
        for expected in expected_categories:
            self.assertIn(expected, category_names)

if __name__ == '__main__':
    unittest.main()

