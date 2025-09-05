#!/usr/bin/env python3
"""
Script de teste para o módulo de processamento de linguagem natural.
"""
import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.nlp.message_processor import MessageProcessor

def test_nlp():
    """Testa o processador de mensagens com diferentes exemplos."""
    
    processor = MessageProcessor()
    
    # Casos de teste para gastos
    expense_messages = [
        "Gastei 50 reais em alimentação",
        "Combustível 120",
        "Paguei 30 no almoço",
        "Comprei roupas por R$ 85,50",
        "Saiu 25 pila no uber",
        "Conta do médico deu 150 reais",
        "R$ 40 na farmácia",
        "Aluguel 800",
        "Gasto com educação: 200 reais"
    ]
    
    # Casos de teste para relatórios
    report_messages = [
        "Relatório alimentação",
        "Quanto gastei este mês",
        "Total de gastos",
        "Resumo transporte",
        "Balanço da semana",
        "Relatório de saúde"
    ]
    
    # Casos de teste para mensagens desconhecidas
    unknown_messages = [
        "Olá, como vai?",
        "Que horas são?",
        "Obrigado pela ajuda",
        "123456"
    ]
    
    print("=== TESTE DO PROCESSADOR DE MENSAGENS ===\n")
    
    print("📊 TESTANDO MENSAGENS DE GASTOS:")
    print("-" * 50)
    for message in expense_messages:
        result = processor.process_message(message)
        print(f"Mensagem: '{message}'")
        print(f"Tipo: {result['type']}")
        if result['type'] == 'expense':
            print(f"Valor: R$ {result.get('amount', 'N/A')}")
            print(f"Categoria: {result.get('category', 'N/A')}")
            print(f"Descrição: {result.get('description', 'N/A')}")
            print(f"Confiança: {result.get('confidence', 0):.2f}")
        print()
    
    print("📈 TESTANDO MENSAGENS DE RELATÓRIOS:")
    print("-" * 50)
    for message in report_messages:
        result = processor.process_message(message)
        print(f"Mensagem: '{message}'")
        print(f"Tipo: {result['type']}")
        if result['type'] == 'report':
            print(f"Categoria: {result.get('category', 'N/A')}")
            print(f"Período: {result.get('period', 'N/A')}")
        print()
    
    print("❓ TESTANDO MENSAGENS DESCONHECIDAS:")
    print("-" * 50)
    for message in unknown_messages:
        result = processor.process_message(message)
        print(f"Mensagem: '{message}'")
        print(f"Tipo: {result['type']}")
        print()
    
    print("✅ TESTE CONCLUÍDO!")
    print(f"Categorias disponíveis: {', '.join(processor.get_categories())}")

if __name__ == "__main__":
    test_nlp()

