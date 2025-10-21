#!/usr/bin/env python3
"""
Script para gerar env.json a partir do arquivo .env

Este script lê o arquivo .env e gera um arquivo env.json no formato
esperado pelo AWS SAM CLI para injetar variáveis de ambiente durante
a execução local da função Lambda.

Uso:
    python scripts/generate_env_json.py
"""

import json
import os
import sys
from pathlib import Path
from dotenv import dotenv_values

# Nome da função Lambda (deve corresponder ao template.yaml)
LAMBDA_FUNCTION_NAME = "FinancialAssistantFunction"

# Arquivos de entrada e saída
ENV_FILE = ".env"
OUTPUT_FILE = "env.json"


def main():
    """Função principal do script."""
    print("🔄 Gerando env.json a partir do .env...")
    
    # Verificar se o arquivo .env existe
    if not os.path.exists(ENV_FILE):
        print(f"❌ Erro: Arquivo '{ENV_FILE}' não encontrado!")
        print(f"   Crie um arquivo .env baseado no .env.example")
        sys.exit(1)
    
    try:
        # Carregar variáveis do .env
        env_vars = dotenv_values(ENV_FILE)
        
        if not env_vars:
            print(f"⚠️  Aviso: Nenhuma variável encontrada no {ENV_FILE}")
        
        # Remover variáveis vazias
        env_vars = {k: v for k, v in env_vars.items() if v}
        
        # Formato esperado pelo SAM CLI
        env_json = {
            LAMBDA_FUNCTION_NAME: env_vars
        }
        
        # Escrever arquivo env.json
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(env_json, f, indent=2)
        
        print(f"✅ Arquivo '{OUTPUT_FILE}' gerado com sucesso!")
        print(f"   {len(env_vars)} variáveis de ambiente carregadas")
        
        # Mostrar variáveis (sem valores sensíveis)
        print("\n📋 Variáveis configuradas:")
        for key in sorted(env_vars.keys()):
            # Ocultar valores sensíveis
            if any(secret in key.upper() for secret in [
                'KEY', 'SECRET', 'TOKEN', 'PASSWORD', 'SID'
            ]):
                print(f"   - {key}: ********")
            else:
                print(f"   - {key}: {env_vars[key]}")
        
    except Exception as e:
        print(f"❌ Erro ao gerar env.json: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

