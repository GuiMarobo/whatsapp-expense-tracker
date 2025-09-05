"""
Testes para o módulo de processamento de linguagem natural.
"""
import unittest
import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from src.nlp.message_processor import MessageProcessor

class TestMessageProcessor(unittest.TestCase):
    """Testes para a classe MessageProcessor."""
    
    def setUp(self):
        """Configura o teste."""
        self.processor = MessageProcessor()
    
    def test_expense_message_simple(self):
        """Testa processamento de mensagem de gasto simples."""
        message = "Gastei 50 reais em alimentação"
        result = self.processor.process_message(message)
        
        self.assertEqual(result['type'], 'expense')
        self.assertEqual(result['amount'], 50.0)
        self.assertEqual(result['category'], 'alimentação')
        self.assertGreater(result['confidence'], 0.5)
    
    def test_expense_message_with_currency_symbol(self):
        """Testa processamento com símbolo de moeda."""
        message = "Comprei roupas por R$ 85,50"
        result = self.processor.process_message(message)
        
        self.assertEqual(result['type'], 'expense')
        self.assertEqual(result['amount'], 85.5)
        self.assertEqual(result['category'], 'roupas')
    
    def test_expense_message_implicit(self):
        """Testa gasto implícito (só valor e categoria)."""
        message = "Combustível 120"
        result = self.processor.process_message(message)
        
        self.assertEqual(result['type'], 'expense')
        self.assertEqual(result['amount'], 120.0)
        self.assertIn(result['category'], ['combustível', 'transporte'])
    
    def test_report_message(self):
        """Testa mensagem de relatório."""
        message = "Relatório alimentação"
        result = self.processor.process_message(message)
        
        self.assertEqual(result['type'], 'report')
        self.assertEqual(result['category'], 'alimentação')
        self.assertEqual(result['period'], 'month')
    
    def test_report_message_with_period(self):
        """Testa relatório com período específico."""
        message = "Balanço da semana"
        result = self.processor.process_message(message)
        
        self.assertEqual(result['type'], 'report')
        self.assertEqual(result['period'], 'week')
    
    def test_unknown_message(self):
        """Testa mensagem desconhecida."""
        message = "Olá, como vai?"
        result = self.processor.process_message(message)
        
        self.assertEqual(result['type'], 'unknown')
    
    def test_extract_amount(self):
        """Testa extração de valores monetários."""
        test_cases = [
            ("50 reais", 50.0),
            ("R$ 85,50", 85.5),
            ("120", 120.0),
            ("25 pila", 25.0),
            ("sem valor", None)
        ]
        
        for message, expected in test_cases:
            with self.subTest(message=message):
                result = self.processor._extract_amount(message)
                self.assertEqual(result, expected)
    
    def test_extract_category(self):
        """Testa extração de categorias."""
        test_cases = [
            ("alimentação", "alimentação"),
            ("combustível", "combustível"),
            ("uber", "transporte"),
            ("médico", "saúde"),
            ("faculdade", "educação"),
            ("cinema", "lazer"),
            ("aluguel", "casa"),
            ("camisa", "roupas"),
            ("algo desconhecido", "outros")
        ]
        
        for message, expected in test_cases:
            with self.subTest(message=message):
                result = self.processor._extract_category(message)
                self.assertEqual(result, expected)
    
    def test_validate_message(self):
        """Testa validação de mensagens."""
        # Mensagem válida
        is_valid, error = self.processor.validate_message("Gastei 50 reais")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
        
        # Mensagem vazia
        is_valid, error = self.processor.validate_message("")
        self.assertFalse(is_valid)
        self.assertEqual(error, "Mensagem vazia")
        
        # Mensagem muito longa
        long_message = "a" * 501
        is_valid, error = self.processor.validate_message(long_message)
        self.assertFalse(is_valid)
        self.assertIn("muito longa", error)
    
    def test_confidence_calculation(self):
        """Testa cálculo de confiança."""
        # Alta confiança (valor + categoria específica + descrição)
        high_conf = self.processor._calculate_confidence(50.0, "alimentação", "almoço no restaurante")
        self.assertGreater(high_conf, 0.8)
        
        # Baixa confiança (só valor)
        low_conf = self.processor._calculate_confidence(50.0, None, "")
        self.assertLess(low_conf, 0.5)
        
        # Confiança média (valor + categoria genérica)
        med_conf = self.processor._calculate_confidence(50.0, "outros", "")
        self.assertGreater(med_conf, 0.4)
        self.assertLess(med_conf, 0.8)

if __name__ == '__main__':
    unittest.main()

