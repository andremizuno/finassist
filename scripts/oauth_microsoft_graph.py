#!/usr/bin/env python3
"""
Script interativo para obter tokens OAuth2 do Microsoft Graph.

Este script inicia um servidor web local temporário e guia o usuário
através do fluxo de autenticação OAuth2 para obter um refresh_token
que pode ser usado pela aplicação.

Uso:
    python scripts/oauth_microsoft_graph.py

Pré-requisitos:
    - Aplicação registrada no Azure AD
    - CLIENT_ID e CLIENT_SECRET configurados no .env
    - Redirect URI configurado no Azure AD: http://localhost:8080/callback
"""

import os
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse, urlencode
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações OAuth2
CLIENT_ID = os.getenv('MS_GRAPH_CLIENT_ID')
CLIENT_SECRET = os.getenv('MS_GRAPH_CLIENT_SECRET')
TENANT_ID = os.getenv('MS_GRAPH_TENANT_ID', 'common')
REDIRECT_URI = 'http://localhost:8080/callback'
SCOPES = 'User.Read Files.ReadWrite.All offline_access'

# URLs da Microsoft
AUTH_URL = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize'
TOKEN_URL = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token'

# Variável global para armazenar o código de autorização
authorization_code = None


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handler para processar o callback do OAuth."""
    
    def do_GET(self):
        """Processa requisições GET do callback."""
        global authorization_code
        
        # Parse da URL
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/callback':
            # Extrair parâmetros da query string
            params = parse_qs(parsed_url.query)
            
            if 'code' in params:
                # Código de autorização recebido
                authorization_code = params['code'][0]
                
                # Responder ao navegador
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Autenticação Concluída</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }
                        .container {
                            background: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                            text-align: center;
                        }
                        h1 { color: #667eea; margin-bottom: 20px; }
                        p { color: #666; font-size: 18px; }
                        .success { color: #10b981; font-size: 48px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="success">✓</div>
                        <h1>Autenticação Concluída!</h1>
                        <p>Você pode fechar esta janela e voltar ao terminal.</p>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
            
            elif 'error' in params:
                # Erro na autenticação
                error = params['error'][0]
                error_description = params.get('error_description', [''])[0]
                
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Erro de Autenticação</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                            background: #f3f4f6;
                        }}
                        .container {{
                            background: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                            text-align: center;
                        }}
                        h1 {{ color: #ef4444; margin-bottom: 20px; }}
                        p {{ color: #666; }}
                        .error {{ color: #ef4444; font-size: 48px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="error">✗</div>
                        <h1>Erro na Autenticação</h1>
                        <p><strong>Erro:</strong> {error}</p>
                        <p>{error_description}</p>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
        else:
            # Página não encontrada
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suprimir logs do servidor HTTP."""
        pass


def exchange_code_for_tokens(code):
    """
    Troca o código de autorização por tokens de acesso.
    
    Args:
        code: Código de autorização obtido do callback
    
    Returns:
        dict: Tokens (access_token, refresh_token, etc.)
    """
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code',
        'scope': SCOPES
    }
    
    response = requests.post(TOKEN_URL, data=data)
    response.raise_for_status()
    
    return response.json()


def save_tokens(tokens):
    """
    Salva os tokens no arquivo .ms_graph_tokens.json
    
    Args:
        tokens: Dict com tokens
    """
    import time
    
    token_data = {
        'access_token': tokens.get('access_token'),
        'refresh_token': tokens.get('refresh_token'),
        'expiration_time': time.time() + tokens.get('expires_in', 3600)
    }
    
    with open('.ms_graph_tokens.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print("\n✅ Tokens salvos em .ms_graph_tokens.json")


def main():
    """Função principal do script."""
    print("=" * 70)
    print(" 🔐 Autenticação OAuth2 - Microsoft Graph API")
    print("=" * 70)
    
    # Validar configurações
    if not CLIENT_ID or not CLIENT_SECRET:
        print("\n❌ Erro: CLIENT_ID ou CLIENT_SECRET não configurados no .env")
        print("   Configure as variáveis MS_GRAPH_CLIENT_ID e MS_GRAPH_CLIENT_SECRET")
        return
    
    print(f"\n📋 Configuração:")
    print(f"   Client ID: {CLIENT_ID[:8]}...")
    print(f"   Tenant ID: {TENANT_ID}")
    print(f"   Redirect URI: {REDIRECT_URI}")
    print(f"   Scopes: {SCOPES}")
    
    # Gerar URL de autorização
    auth_params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPES,
        'response_mode': 'query'
    }
    
    auth_url_full = f"{AUTH_URL}?{urlencode(auth_params)}"
    
    print("\n🌐 Iniciando servidor local na porta 8080...")
    print("\n⚡ Um navegador será aberto para autenticação.")
    print("   Faça login com sua conta Microsoft e autorize o aplicativo.")
    print("\n⏳ Aguardando autenticação...")
    
    # Iniciar servidor HTTP
    server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)
    
    # Abrir navegador
    webbrowser.open(auth_url_full)
    
    # Aguardar callback (processa uma única requisição)
    server.handle_request()
    
    # Verificar se recebemos o código
    if authorization_code:
        print("\n✅ Código de autorização recebido!")
        print("\n🔄 Trocando código por tokens...")
        
        try:
            tokens = exchange_code_for_tokens(authorization_code)
            
            print("\n✅ Tokens obtidos com sucesso!")
            print(f"\n📝 Refresh Token (adicione ao .env):")
            print(f"   MS_GRAPH_REFRESH_TOKEN={tokens.get('refresh_token')}")
            
            # Salvar tokens
            save_tokens(tokens)
            
            print("\n✨ Processo concluído com sucesso!")
            print("\n📖 Próximos passos:")
            print("   1. Adicione o refresh_token ao seu arquivo .env")
            print("   2. Execute 'make generate-env-json' para atualizar env.json")
            print("   3. Inicie a aplicação com 'make start-api'")
            
        except Exception as e:
            print(f"\n❌ Erro ao trocar código por tokens: {str(e)}")
    else:
        print("\n❌ Falha ao obter código de autorização")
    
    # Fechar servidor
    server.server_close()
    print("\n🛑 Servidor local encerrado.")


if __name__ == '__main__':
    main()

