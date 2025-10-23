# ✅ DynamoDB Local - SOLUÇÃO COMPLETA

## 🎯 Problema Identificado

**Dois problemas distintos:**

1. **boto3 travava antes de conectar** - Problema com busca de metadados EC2
2. **DynamoDB não respondia** - Volume persistente com erro de permissões sqlite

## ✅ Solução Implementada

### 1. Correções no Código Python

Adicionar ANTES de importar boto3:

```python
import os
os.environ['AWS_EC2_METADATA_DISABLED'] = 'true'
os.environ['AWS_CONFIG_FILE'] = '/dev/null'
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = os.path.expanduser('~/.aws/credentials')

import boto3
from botocore.config import Config

config = Config(
    region_name='us-east-1',
    signature_version='v4',
    retries={'max_attempts': 0},
    connect_timeout=5,
    read_timeout=5
)

client = boto3.client(
    'dynamodb',
    endpoint_url='http://127.0.0.1:8000',
    aws_access_key_id='fakeMyKeyId',
    aws_secret_access_key='fakeSecretAccessKey',
    region_name='us-east-1',
    config=config
)
```

### 2. Arquivos AWS Config

**~/.aws/credentials:**
```ini
[default]
aws_access_key_id=fakeMyKeyId
aws_secret_access_key=fakeSecretAccessKey
```

**~/.aws/config:**
```ini
[default]
region=us-east-1
```

### 3. DynamoDB com Persistência em Disco (WSL2)

**Problema:** Volume Docker padrão apresentava erro de permissões no sqlite dentro do WSL2.

**Solução:** Mapear volume para filesystem do WSL2 (NÃO usar /mnt/c):

```bash
# Criar diretório de dados no WSL2
mkdir -p ~/dynamodb_data
chmod 777 ~/dynamodb_data

# Iniciar com volume persistente correto
docker run -d --name finassist-dynamodb-local \
  -p 8000:8000 \
  -v ~/dynamodb_data:/data \
  amazon/dynamodb-local:latest \
  -jar DynamoDBLocal.jar -sharedDb -dbPath /data
```

**⚠️ CRÍTICO:** NUNCA use `/mnt/c/` ou caminhos do Windows. Sempre use caminhos do WSL2 (`~/` ou `/home/usuario/`).

### 4. Downgrade do boto3

**Versão que funcionou:** boto3==1.28.85, botocore==1.31.85

```bash
pip install 'boto3==1.28.85' 'botocore==1.31.85'
```

## 📋 Checklist de Verificação

- [x] Socket TCP puro conecta em <1s ✅
- [x] curl funciona ✅  
- [x] Arquivos ~/.aws/credentials e ~/.aws/config criados ✅
- [x] AWS_EC2_METADATA_DISABLED=true exportado ✅
- [x] boto3 downgrade para 1.28.85 ✅
- [x] DynamoDB com persistência em disco WSL2 ✅
- [x] boto3.client().list_tables() funciona ✅
- [x] Tabela 'FinancialAssistantThreads' criada ✅
- [x] Dados persistem após restart do container ✅

## 🚀 Como Usar

### Iniciar DynamoDB Local (com Persistência)

```bash
# Criar diretório de dados (apenas primeira vez)
mkdir -p ~/dynamodb_data
chmod 777 ~/dynamodb_data

# Iniciar container
docker run -d --name finassist-dynamodb-local \
  -p 8000:8000 \
  -v ~/dynamodb_data:/data \
  amazon/dynamodb-local:latest \
  -jar DynamoDBLocal.jar -sharedDb -dbPath /data

# Ou usar docker-compose
docker-compose up -d dynamodb-local
```

### Em Scripts Python

```python
#!/usr/bin/env python3
import os
os.environ['AWS_EC2_METADATA_DISABLED'] = 'true'

import boto3

client = boto3.client(
    'dynamodb',
    endpoint_url='http://127.0.0.1:8000',
    aws_access_key_id='fakeMyKeyId',
    aws_secret_access_key='fakeSecretAccessKey',
    region_name='us-east-1'
)

# Funciona!
print(client.list_tables())
```

## ✅ Benefícios da Persistência em Disco

- **Dados persistem** entre reinicializações ✅
- **Desenvolvimento mais realista** ✅
- **Não precisa recriar tabelas** a cada restart ✅
- **Arquivos armazenados em:** `~/dynamodb_data/shared-local-instance.db`

## ⚠️ Cuidados Importantes no WSL2

1. **NUNCA use `/mnt/c/` ou caminhos do Windows** - causa erro sqlite
2. **SEMPRE use caminhos do WSL2** (`~/ ou `/home/usuario/`)
3. **Permissões:** `chmod 777` no diretório de dados
4. **Verificar:** `docker exec container bash -c "touch /data/teste"` deve funcionar

## 📝 Próximos Passos

1. ✅ docker-compose.yml atualizado com volume correto
2. ✅ Persistência funcionando perfeitamente
3. ⏭️ Documentar no README.md

## 🎉 Status Final

**✅ FUNCIONANDO PERFEITAMENTE!**

```bash
$ python3 test_boto3_fixed.py
Configurando cliente...
Listando tabelas...
✅ SUCESSO! Tabelas: ['FinancialAssistantThreads']
```

---

**Data:** 23/10/2025
**Versões:** boto3==1.28.85, botocore==1.31.85, Python 3.12.3, WSL2
