#!/usr/bin/env python3
"""
Script de teste para o webhook do WhatsApp.
"""
import requests
import json
import sys
import os


# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_webhook_locally():
    """Testa o webhook localmente."""
    
    base_url = "http://localhost:50001/api"
    
    # Casos de teste
    test_cases = [
        {
            "name": "Gasto simples",
            "message": "Gastei 50 reais em alimentação",
            "phone": "5511999999999"
        },
        {
            "name": "Gasto com combustível",
            "message": "Combustível 120",
            "phone": "5511999999999"
        },
        {
            "name": "Relatório",
            "message": "Relatório alimentação",
            "phone": "5511999999999"
        },
        {
            "name": "Ajuda",
            "message": "ajuda",
            "phone": "5511999999999"
        },
        {
            "name": "Estatísticas",
            "message": "estatisticas",
            "phone": "5511999999999"
        }
    ]
    
    print("=== TESTE DO WEBHOOK ===\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. Testando: {test_case['name']}")
        print(f"   Mensagem: '{test_case['message']}'")
        
        try:
            response = requests.post(
                f"{base_url}/webhook/test",
                json={
                    "message": test_case['message'],
                    "phone": test_case['phone']
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Sucesso: {data.get('message', 'OK')}")
                if 'response' in data:
                    print(f"   📱 Resposta: {data['response'][:100]}...")
            else:
                print(f"   ❌ Erro {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Erro: Servidor não está rodando. Execute 'python src/main.py' primeiro.")
            return False
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
        
        print()
    
    return True

def test_health_check():
    """Testa o endpoint de health check."""
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check OK: {data}")
            return True
        else:
            print(f"❌ Health Check falhou: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando")
        return False
    except Exception as e:
        print(f"❌ Erro no health check: {str(e)}")
        return False

if __name__ == "__main__":
    print("Verificando se o servidor está rodando...")
    
    if test_health_check():
        print("\nIniciando testes do webhook...\n")
        test_webhook_locally()
    else:
        print("\nPara executar os testes:")
        print("1. Execute: python src/main.py")
        print("2. Em outro terminal, execute: python test_webhook.py")

