#!/usr/bin/env python3
"""
Script para criar um OpenAI Assistant com as configurações necessárias.

Este script facilita a criação do Assistant na OpenAI Platform com todas
as ferramentas e instruções necessárias para o Assistente Financeiro.

Uso:
    python scripts/create_assistant.py
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Instruções do Assistant
ASSISTANT_INSTRUCTIONS = """
Você é um assistente financeiro pessoal inteligente e amigável.

Suas responsabilidades:
1. Ajudar o usuário a registrar despesas e receitas
2. Fornecer análises e insights sobre gastos
3. Responder perguntas sobre finanças pessoais
4. Ser proativo em sugerir economia e melhores práticas

Diretrizes:
- Seja sempre educado e empático
- Use linguagem clara e acessível
- Peça confirmação antes de registrar despesas
- Forneça resumos claros quando solicitado
- Use emojis quando apropriado (💰 📊 ✅)

Formato de dados:
- Datas: YYYY-MM-DD
- Valores: sempre em R$ (reais brasileiros)
- Categorias comuns: Alimentação, Transporte, Moradia, Lazer, Saúde, Educação, Outros
"""

# Definição das ferramentas (tools)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_expense",
            "description": "Adiciona uma nova despesa à planilha de controle financeiro",
            "parameters": {
                "type": "object",
                "properties": {
                    "workbook_id": {
                        "type": "string",
                        "description": "ID do arquivo Excel no OneDrive"
                    },
                    "worksheet_name": {
                        "type": "string",
                        "description": "Nome da planilha/aba (ex: 'Despesas')"
                    },
                    "date": {
                        "type": "string",
                        "description": "Data da despesa no formato YYYY-MM-DD"
                    },
                    "description": {
                        "type": "string",
                        "description": "Descrição da despesa"
                    },
                    "category": {
                        "type": "string",
                        "description": "Categoria da despesa (ex: Alimentação, Transporte)"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Valor da despesa em reais"
                    }
                },
                "required": ["workbook_id", "worksheet_name", "date", "description", "category", "amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_expense_history",
            "description": "Recupera histórico de despesas da planilha",
            "parameters": {
                "type": "object",
                "properties": {
                    "workbook_id": {
                        "type": "string",
                        "description": "ID do arquivo Excel no OneDrive"
                    },
                    "worksheet_name": {
                        "type": "string",
                        "description": "Nome da planilha/aba"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Filtros opcionais (ex: {'category': 'Alimentação'})",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Filtrar por categoria"
                            }
                        }
                    }
                },
                "required": ["workbook_id", "worksheet_name"]
            }
        }
    }
]


def create_assistant():
    """Cria o Assistant na OpenAI Platform."""
    
    print("=" * 70)
    print(" 🤖 Criando OpenAI Assistant")
    print("=" * 70)
    
    # Verificar API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\n❌ Erro: OPENAI_API_KEY não encontrada no .env")
        return
    
    print(f"\n✓ API Key encontrada: {api_key[:10]}...")
    
    # Inicializar cliente
    client = OpenAI(api_key=api_key)
    
    print("\n📋 Configuração do Assistant:")
    print(f"  - Nome: Assistente Financeiro")
    print(f"  - Modelo: gpt-4-turbo-preview")
    print(f"  - Ferramentas: {len(TOOLS)}")
    
    try:
        # Criar Assistant
        print("\n🔄 Criando Assistant na OpenAI Platform...")
        
        assistant = client.beta.assistants.create(
            name="Assistente Financeiro",
            instructions=ASSISTANT_INSTRUCTIONS,
            model="gpt-4-turbo-preview",
            tools=TOOLS
        )
        
        print("\n✅ Assistant criado com sucesso!")
        print(f"\n📝 ASSISTANT_ID: {assistant.id}")
        print("\n⚠️  IMPORTANTE: Adicione este ID ao seu arquivo .env:")
        print(f"   ASSISTANT_ID={assistant.id}")
        
        print("\n📊 Detalhes:")
        print(f"  - ID: {assistant.id}")
        print(f"  - Nome: {assistant.name}")
        print(f"  - Modelo: {assistant.model}")
        print(f"  - Ferramentas: {len(assistant.tools)}")
        
        print("\n✨ Pronto! Agora você pode usar o assistente.")
        
    except Exception as e:
        print(f"\n❌ Erro ao criar Assistant: {str(e)}")


if __name__ == '__main__':
    create_assistant()

