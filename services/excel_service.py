"""
Serviço para interação com Microsoft Graph API (Excel).

Este módulo gerencia a autenticação OAuth2 com o Microsoft Graph
e fornece métodos para manipular planilhas Excel no OneDrive.
Inclui gerenciamento automático de tokens (refresh quando expiram).
"""

import os
import time
import json
import requests
from typing import Dict, Any, List, Optional

from config.settings import (
    MS_GRAPH_CLIENT_ID,
    MS_GRAPH_CLIENT_SECRET,
    MS_GRAPH_TENANT_ID,
    MS_GRAPH_REFRESH_TOKEN,
    MS_GRAPH_ACCESS_TOKEN,
    MS_GRAPH_TOKEN_EXPIRATION_INITIAL
)
from utils.logger import setup_logger
from utils.exceptions import MicrosoftGraphAPIError

# Logger específico deste módulo
logger = setup_logger(__name__)

# Arquivo local para persistir tokens (apenas para desenvolvimento local)
# NÃO USAR EM PRODUÇÃO! Em produção, use AWS Secrets Manager ou similar
LOCAL_TOKEN_FILE = ".ms_graph_tokens.json"


class ExcelService:
    """
    Serviço responsável por interagir com a Microsoft Graph API para Excel.
    
    Gerencia autenticação OAuth2, refresh automático de tokens e
    operações CRUD em planilhas Excel no OneDrive.
    """
    
    def __init__(self):
        """Inicializa o serviço e carrega/atualiza tokens."""
        # Variáveis de instância para tokens
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiration_time: float = 0
        
        # Carregar tokens de forma segura
        self._load_tokens_securely()
        
        logger.info("Excel Service inicializado")
    
    def _load_tokens_securely(self) -> None:
        """
        Carrega tokens do arquivo local ou variáveis de ambiente.
        
        Para desenvolvimento local: tenta carregar do arquivo de tokens,
        senão usa os do .env e tenta fazer refresh se necessário.
        """
        # Tentar carregar do arquivo local primeiro
        if os.path.exists(LOCAL_TOKEN_FILE):
            try:
                with open(LOCAL_TOKEN_FILE, 'r') as f:
                    tokens = json.load(f)
                    self.access_token = tokens.get('access_token')
                    self.refresh_token = tokens.get('refresh_token')
                    self.token_expiration_time = tokens.get('expiration_time', 0)
                logger.info("Tokens do Microsoft Graph carregados do arquivo local")
            except Exception as e:
                logger.warning(
                    f"Falha ao carregar tokens locais: {e}. "
                    "Usando variáveis de ambiente."
                )
        
        # Se ainda não tem tokens, usar do ambiente
        if not self.refresh_token and MS_GRAPH_REFRESH_TOKEN:
            self.refresh_token = MS_GRAPH_REFRESH_TOKEN
        
        if not self.access_token and MS_GRAPH_ACCESS_TOKEN:
            self.access_token = MS_GRAPH_ACCESS_TOKEN
        
        if self.token_expiration_time == 0 and MS_GRAPH_TOKEN_EXPIRATION_INITIAL:
            # Converter tempo de expiração inicial para timestamp futuro
            self.token_expiration_time = (
                time.time() + int(MS_GRAPH_TOKEN_EXPIRATION_INITIAL)
            )
        
        # Se o access token está ausente ou expirando, fazer refresh
        if self.refresh_token and (
            not self.access_token or 
            self.token_expiration_time < time.time() + 300  # 5 minutos
        ):
            logger.info(
                "Access token ausente ou expirando em breve. "
                "Fazendo refresh..."
            )
            self._refresh_access_token()
    
    def _save_tokens_securely(self) -> None:
        """
        Persiste tokens atualizados no arquivo local.
        
        ATENÇÃO: Apenas para desenvolvimento local!
        Em produção, use AWS Secrets Manager, Parameter Store ou similar.
        """
        try:
            tokens = {
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'expiration_time': self.token_expiration_time
            }
            
            with open(LOCAL_TOKEN_FILE, 'w') as f:
                json.dump(tokens, f)
            
            logger.info("Tokens do Microsoft Graph salvos no arquivo local")
        except Exception as e:
            logger.error(f"Erro ao salvar tokens localmente: {e}")
    
    def _refresh_access_token(self) -> None:
        """
        Obtém um novo access token usando o refresh token.
        
        Raises:
            MicrosoftGraphAPIError: Se o refresh falhar
        """
        if not self.refresh_token:
            raise MicrosoftGraphAPIError(
                "Nenhum refresh token disponível. "
                "Execute o fluxo OAuth inicial para obter um."
            )
        
        token_url = (
            f"https://login.microsoftonline.com/{MS_GRAPH_TENANT_ID}"
            "/oauth2/v2.0/token"
        )
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        data = {
            'client_id': MS_GRAPH_CLIENT_ID,
            'client_secret': MS_GRAPH_CLIENT_SECRET,
            'scope': 'User.Read Files.ReadWrite.All offline_access',
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        
        try:
            logger.debug("Requisitando novo access token...")
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Atualizar tokens
            self.access_token = token_data['access_token']
            
            # Refresh token pode ou não ser atualizado
            if 'refresh_token' in token_data:
                self.refresh_token = token_data['refresh_token']
            
            # Calcular tempo de expiração
            expires_in = token_data.get('expires_in', 3600)
            self.token_expiration_time = time.time() + expires_in
            
            # Salvar tokens atualizados
            self._save_tokens_securely()
            
            logger.info("Access token do Microsoft Graph renovado com sucesso")
            
        except requests.exceptions.RequestException as e:
            error_text = e.response.text if e.response else str(e)
            logger.error(f"Erro ao renovar access token: {error_text}")
            raise MicrosoftGraphAPIError(
                f"Falha ao renovar access token: {error_text}"
            ) from e
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Retorna headers HTTP com token de autenticação válido.
        
        Verifica se o token está próximo de expirar e faz refresh se necessário.
        
        Returns:
            dict: Headers HTTP com Authorization
        """
        # Verificar se precisa fazer refresh (< 1 minuto para expirar)
        if not self.access_token or self.token_expiration_time < time.time() + 60:
            logger.info(
                "Access token ausente ou próximo de expirar. "
                "Fazendo refresh..."
            )
            self._refresh_access_token()
        
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def add_expense(
        self,
        workbook_id: str,
        worksheet_name: str,
        expense_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adiciona uma despesa à planilha Excel.
        
        Args:
            workbook_id: ID do workbook (arquivo Excel) no OneDrive
            worksheet_name: Nome da planilha (aba)
            expense_data: Dados da despesa. Exemplo:
                          {
                              'date': '2025-10-21',
                              'description': 'Almoço',
                              'category': 'Alimentação',
                              'amount': 45.00
                          }
        
        Returns:
            dict: Resposta da API com informações sobre a operação
            
        Raises:
            MicrosoftGraphAPIError: Se houver erro ao adicionar despesa
        """
        try:
            logger.debug(
                f"Adicionando despesa ao workbook {workbook_id}, "
                f"planilha {worksheet_name}"
            )
            
            # Endpoint para adicionar linha à tabela
            # NOTA: Este é um exemplo. Você precisará ajustar conforme
            # a estrutura da sua planilha e se está usando uma Table ou Range
            url = (
                f"https://graph.microsoft.com/v1.0/me/drive/items/{workbook_id}"
                f"/workbook/worksheets/{worksheet_name}/range"
            )
            
            # Preparar dados para adicionar
            # Formato: array de valores para adicionar como nova linha
            values = [[
                expense_data.get('date', ''),
                expense_data.get('description', ''),
                expense_data.get('category', ''),
                expense_data.get('amount', 0)
            ]]
            
            # Aqui você precisará adaptar para sua estrutura específica
            # Exemplo: adicionar à próxima linha vazia
            # Por simplicidade, este é um exemplo conceitual
            
            payload = {
                'values': values
            }
            
            headers = self._get_headers()
            response = requests.patch(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info("Despesa adicionada com sucesso ao Excel")
            
            return result
            
        except requests.exceptions.RequestException as e:
            error_text = e.response.text if e.response else str(e)
            logger.error(f"Erro ao adicionar despesa: {error_text}")
            raise MicrosoftGraphAPIError(
                f"Falha ao adicionar despesa: {error_text}"
            ) from e
    
    def get_expense_history(
        self,
        workbook_id: str,
        worksheet_name: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recupera histórico de despesas da planilha Excel.
        
        Args:
            workbook_id: ID do workbook no OneDrive
            worksheet_name: Nome da planilha
            filters: Filtros opcionais (ex: {'category': 'Alimentação'})
        
        Returns:
            list: Lista de despesas, cada uma como dict
            
        Raises:
            MicrosoftGraphAPIError: Se houver erro ao buscar despesas
        """
        try:
            logger.debug(
                f"Recuperando despesas do workbook {workbook_id}, "
                f"planilha {worksheet_name}"
            )
            
            # Endpoint para ler range ou tabela
            # NOTA: Adaptar conforme sua estrutura
            url = (
                f"https://graph.microsoft.com/v1.0/me/drive/items/{workbook_id}"
                f"/workbook/worksheets/{worksheet_name}/usedRange"
            )
            
            headers = self._get_headers()
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Processar dados (assumindo formato: data, descrição, categoria, valor)
            values = data.get('values', [])
            
            # Primeira linha geralmente é cabeçalho
            if not values or len(values) < 2:
                logger.info("Nenhuma despesa encontrada")
                return []
            
            headers_row = values[0]
            expenses = []
            
            for row in values[1:]:
                if len(row) >= 4:  # Garantir que tem dados suficientes
                    expense = {
                        'date': row[0],
                        'description': row[1],
                        'category': row[2],
                        'amount': row[3]
                    }
                    expenses.append(expense)
            
            logger.info(f"{len(expenses)} despesas recuperadas do Excel")
            
            # Aplicar filtros se fornecidos
            if filters:
                expenses = [
                    exp for exp in expenses
                    if all(exp.get(k) == v for k, v in filters.items())
                ]
                logger.debug(
                    f"{len(expenses)} despesas após aplicar filtros"
                )
            
            return expenses
            
        except requests.exceptions.RequestException as e:
            error_text = e.response.text if e.response else str(e)
            logger.error(f"Erro ao recuperar despesas: {error_text}")
            raise MicrosoftGraphAPIError(
                f"Falha ao recuperar despesas: {error_text}"
            ) from e


# Instância global do serviço (singleton pattern)
excel_service = ExcelService()

