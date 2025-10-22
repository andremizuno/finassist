"""
Serviço para processamento de mensagens de áudio.

Este módulo é responsável por baixar arquivos de áudio de URLs do Twilio
e transcrevê-los usando a API Whisper da OpenAI.
"""

import io
import requests
from typing import Optional

from openai import OpenAI
from config.settings import OPENAI_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from utils.logger import setup_logger
from utils.exceptions import FinancialAssistantError

# Logger específico deste módulo
logger = setup_logger(__name__)


class AudioService:
    """
    Serviço responsável por processar mensagens de áudio do WhatsApp.

    Realiza download de arquivos de áudio das URLs do Twilio e
    transcreve usando a API Whisper da OpenAI.
    """

    def __init__(self):
        """Inicializa o serviço de áudio."""
        if not OPENAI_API_KEY:
            raise FinancialAssistantError("OPENAI_API_KEY não está configurada")

        self.client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("AudioService inicializado")

    def download_audio(self, media_url: str) -> bytes:
        """
        Baixa o arquivo de áudio da URL fornecida pelo Twilio.

        O Twilio requer autenticação HTTP Basic usando Account SID e Auth Token
        para acessar as URLs de mídia.

        Args:
            media_url: URL completa do arquivo de mídia fornecida pelo Twilio

        Returns:
            bytes: Conteúdo binário do arquivo de áudio

        Raises:
            FinancialAssistantError: Se houver erro no download
        """
        try:
            logger.debug(f"Baixando áudio de: {media_url[:50]}...")

            # Twilio requer autenticação HTTP Basic com Account SID e Auth Token
            auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

            # Fazer requisição HTTP GET para baixar o áudio
            response = requests.get(media_url, auth=auth, timeout=30)  # Timeout de 30 segundos

            # Verificar se a requisição foi bem-sucedida
            response.raise_for_status()

            audio_data = response.content
            logger.info(f"Áudio baixado com sucesso. Tamanho: {len(audio_data)} bytes")

            return audio_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao baixar áudio: {str(e)}")
            raise FinancialAssistantError(f"Falha ao baixar arquivo de áudio: {str(e)}") from e

    def transcribe_audio(self, audio_data: bytes, filename: str = "audio.ogg") -> str:
        """
        Transcreve o áudio usando a API Whisper da OpenAI.

        O Whisper suporta diversos formatos de áudio incluindo:
        ogg, mp3, mp4, mpeg, mpga, m4a, wav, webm

        Args:
            audio_data: Dados binários do arquivo de áudio
            filename: Nome do arquivo (usado para indicar formato)
                     Padrão: "audio.ogg" (formato usado pelo WhatsApp)

        Returns:
            str: Texto transcrito do áudio

        Raises:
            FinancialAssistantError: Se houver erro na transcrição
        """
        try:
            logger.debug(f"Transcrevendo áudio usando Whisper API. " f"Tamanho: {len(audio_data)} bytes")

            # Criar um objeto file-like a partir dos bytes
            audio_file = io.BytesIO(audio_data)
            audio_file.name = filename  # Whisper usa o nome para detectar formato

            # Chamar API Whisper para transcrição
            # Usando modelo padrão "whisper-1"
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1", file=audio_file, language="pt"  # Forçar português brasileiro
            )

            # Extrair texto transcrito
            transcribed_text = transcript.text.strip()

            logger.info(f"Áudio transcrito com sucesso. " f"Comprimento do texto: {len(transcribed_text)} caracteres")
            logger.debug(f"Transcrição: {transcribed_text[:100]}...")

            return transcribed_text

        except Exception as e:
            logger.error(f"Erro ao transcrever áudio: {str(e)}")
            raise FinancialAssistantError(f"Falha ao transcrever áudio: {str(e)}") from e

    def process_audio_message(self, media_url: str) -> str:
        """
        Processa uma mensagem de áudio completa: baixa e transcreve.

        Este é o método principal que orquestra todo o fluxo de
        processamento de áudio.

        Args:
            media_url: URL do arquivo de mídia fornecida pelo Twilio

        Returns:
            str: Texto transcrito do áudio

        Raises:
            FinancialAssistantError: Se houver erro no processamento
        """
        logger.info("Processando mensagem de áudio")

        try:
            # Etapa 1: Baixar o áudio
            audio_data = self.download_audio(media_url)

            # Etapa 2: Transcrever usando Whisper
            # WhatsApp via Twilio geralmente envia em formato OGG
            transcription = self.transcribe_audio(audio_data, filename="audio.ogg")

            logger.info("Mensagem de áudio processada com sucesso")
            return transcription

        except FinancialAssistantError:
            # Re-lançar erros conhecidos
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao processar áudio: {str(e)}")
            raise FinancialAssistantError("Erro ao processar mensagem de áudio") from e


# Instância global do serviço (singleton pattern)
audio_service = AudioService()
