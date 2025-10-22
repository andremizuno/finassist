# 🚀 Guia Rápido de Início

Este guia mostra como colocar o Assistente Financeiro rodando localmente em 5 minutos.

## Pré-requisitos Mínimos

- Python 3.9+
- Docker Desktop
- Conta OpenAI (gratuita para testes)
- Conta Twilio (gratuita para sandbox)

## Passo a Passo Rápido

### 1. Setup Inicial (2 minutos)

```bash
# Clonar e entrar no diretório
cd finassist

# Configurar ambiente
make setup

# Ativar ambiente virtual
source .venv/bin/activate  # Linux/macOS
```

### 2. Configurar Credenciais (2 minutos)

```bash
# Copiar template de configuração
cp env.example .env

# Editar com suas credenciais mínimas
nano .env
```

**Credenciais mínimas necessárias:**

```env
# OpenAI (obter em: https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-...
ASSISTANT_ID=asst_...

# Twilio Sandbox (obter em: https://console.twilio.com)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

**Nota:** As credenciais do Microsoft Graph são opcionais para testes iniciais.

### 3. Iniciar Serviços (1 minuto)

Em **3 terminais diferentes**:

**Terminal 1 - DynamoDB:**
```bash
make start-dynamodb-local
```

**Terminal 2 - API:**
```bash
make generate-env-json
make start-api
```

**Terminal 3 - ngrok:**
```bash
make start-ngrok
# Copie a URL HTTPS exibida
```

### 4. Configurar Webhook Twilio (<1 minuto)

1. Acesse https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Em "Sandbox Settings" → "When a message comes in"
3. Cole: `https://SUA-URL-NGROK.app/webhook/whatsapp`
4. Método: POST
5. Salve

### 5. Testar! 🎉

Envie uma mensagem WhatsApp para o número do Twilio:

```
Olá!
```

Você receberá uma resposta do assistente!

**Dica:** Você também pode enviar **mensagens de voz** - elas serão automaticamente transcritas e processadas!

## Comandos Úteis

```bash
# Ver todos os comandos disponíveis
make help

# Executar testes
make test

# Limpar tudo e recomeçar
make clean
make setup
```

## Problemas Comuns

### "Table does not exist"
```bash
make create-dynamodb-table
```

### "OPENAI_API_KEY not configured"
```bash
# Verificar .env e regenerar
make generate-env-json
```

### Twilio não recebe mensagens
- Verificar se ngrok está rodando
- Verificar URL do webhook no Twilio
- Verificar logs do SAM CLI

## Próximos Passos

- Ler [README.md](README.md) completo
- Configurar Microsoft Graph para persistência real
- Customizar o Assistant na OpenAI Platform
- Fazer deploy em produção: `make deploy`

## Suporte

Problemas? Consulte o [README.md](README.md) seção Troubleshooting.

