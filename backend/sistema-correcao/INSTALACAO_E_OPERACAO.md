# Instalação e Operação

## Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)
- Arquivo de imagem de teste (formato JPEG ou PNG)

## Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Arquivo requirements.txt

Criar arquivo `requirements.txt` na raiz do projeto:

```
Flask==2.3.2
opencv-python==4.8.0.74
numpy==1.24.3
colorama==0.4.6
requests==2.31.0
Werkzeug==2.3.6
```

### 3. Instalação Manual

```bash
pip install Flask
pip install opencv-python
pip install numpy
pip install colorama
pip install requests
```

## Configuração

### API (app.py)

Editar valores em `app.py`:

```python
app.run(
    debug=True,           # False em produção
    host='0.0.0.0',      # Aceita conexões externas
    port=5000             # Alterar porta conforme necessário
)
```

### Testes (teste.py)

Configuração disponível no início do arquivo:

```python
QUANTIDADE_REQUISICOES = 100      # Número de testes
ARQUIVO_IMAGEM = 'teste.png'      # Arquivo para teste
URL_API = 'http://localhost:5000/processar'
MODO_TESTE = 'direto'             # 'direto' ou 'api'
THREADS_PARALELAS = 8             # Para modo API
```

## Operação

### Iniciar a API

```bash
python app.py
```

**Saída esperada:**
```
WARNING in flask.app: This is a development server. Do not use it in production applications.
Use a production WSGI server instead.
Press CTRL+C to quit.
```

A API estará disponível em `http://localhost:5000`

### Testar Conectividade

```bash
curl http://localhost:5000/health
```

**Resposta esperada:**
```json
{"status":"ok"}
```

### Processar Gabarito via cURL

```bash
curl -X POST -F "imagem=@gabarito.png" http://localhost:5000/processar
```

**Resposta esperada:**
```json
{
  "qrcode": "665f1a2b8c1234567890abcd",
  "respostas": {
    "1": "A",
    "2": "B",
    "3": "C",
    "4": "D",
    "5": "E",
    "6": "A",
    "7": "B",
    "8": "C",
    "9": "D",
    "10": "E"
  }
}
```

### Processar Gabarito via Python

```python
import requests

with open('gabarito.png', 'rb') as f:
    files = {'imagem': f}
    response = requests.post('http://localhost:5000/processar', files=files)
    
print(response.json())
```

### Executar Testes de Performance

**Modo Direto (sem HTTP):**

```bash
python teste.py
```

**Modo API:**

Editar `teste.py`:
```python
MODO_TESTE = 'api'
```

Depois executar:
```bash
# Terminal 1: iniciar API
python app.py

# Terminal 2: executar testes
python teste.py
```

### Modo Debug/Desenvolvimento

**Teste direto de funções:**

```python
from image_processor import processar_imagem
from data_extractor import extrair_dados

# Carregar imagem
with open('gabarito.png', 'rb') as f:
    imagem_bytes = f.read()

# Processar
gabarito = processar_imagem(imagem_bytes)

# Extrair dados
resultado = extrair_dados(gabarito)

# Inspecionar
print(f"QR Code: {resultado['qrcode']}")
print(f"Respostas: {resultado['respostas']}")

# Debug: salvar imagem processada
import cv2
cv2.imwrite('debug_gabarito.png', gabarito)
```

## Preparação de Imagens de Teste

### Características Ideais

- Formato: JPEG, PNG
- Resolução: 640x480 ou superior
- Ângulo: frontal, máximo 45°
- Iluminação: uniforme, sem sombras
- Gabarito: legível, bem impresso
- QR Code: intacto e legível

### Problemas Comuns

| Problema | Solução |
|----------|---------|
| "Nenhuma imagem enviada" | Verificar campo `imagem` na requisição |
| Gabarito não detectado | Aumentar iluminação ou aproximar câmera |
| Respostas ambíguas | Limpar resposta e remarcar |
| QR Code não lido | Certificar que QR está visível e não danificado |

## Variáveis de Ambiente

Pode ser configurado para aceitar variáveis de ambiente:

```python
import os

PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
HOST = os.getenv('HOST', '0.0.0.0')

app.run(debug=DEBUG, host=HOST, port=PORT)
```

**Uso:**

```bash
PORT=8080 DEBUG=False python app.py
```

## Produção

### Usando Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Parâmetros:**
- `-w 4`: 4 worker processes
- `-b 0.0.0.0:5000`: bind em interface 0.0.0.0 porta 5000

### Usando Waitress

```bash
pip install waitress
waitress-serve --port=5000 app:app
```

### Usando uWSGI

```bash
pip install uwsgi
uwsgi --http :5000 --wsgi-file app.py --callable app --processes 4 --threads 2
```

## Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'cv2'"

**Solução:**
```bash
pip install opencv-python
```

### Erro: "ModuleNotFoundError: No module named 'flask'"

**Solução:**
```bash
pip install flask
```

### Erro: "Porta 5000 já em uso"

**Solução 1 - Mudar porta:**
```python
app.run(port=5001)
```

**Solução 2 - Liberar porta (Linux/Mac):**
```bash
lsof -i :5000
kill -9 <PID>
```

**Solução 2 - Liberar porta (Windows):**
```cmd
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Erro: "ValueError: Erro ao decodificar imagem"

**Causas possíveis:**
- Arquivo corrompido
- Arquivo não é uma imagem válida
- Formato não suportado

**Solução:**
- Converter imagem para PNG/JPEG
- Usar ferramenta de validação de imagem

### Erro: "Timeout na requisição"

**Causas possíveis:**
- Imagem muito grande
- Servidor sobrecarregado
- Conexão lenta

**Solução:**
- Reduzir tamanho da imagem
- Aumentar timeout na requisição
- Escalar servidor

## Monitoramento

### Logs da API

Flask gera logs automaticamente. Para capturar em arquivo:

```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
```

### Métricas de Performance

O script `teste.py` fornece métricas:

```
Tempo por correção: 0.85ms
Correções por segundo: 1176.47 req/s
```

### Health Check

Verificar status regularmente:

```bash
watch -n 5 'curl -s http://localhost:5000/health'
```

## Integração com Sistemas Externos

### Integração com Banco de Dados

```python
import sqlite3

def salvar_resultado(qrcode, respostas):
    conn = sqlite3.connect('gabaritos.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO respostas (qrcode, dados)
        VALUES (?, ?)
    ''', (qrcode, json.dumps(respostas)))
    
    conn.commit()
    conn.close()
```

### Integração com Fila de Mensagens

```python
from celery import Celery

celery_app = Celery('gabaritos')

@celery_app.task
def processar_gabarito_async(imagem_base64):
    imagem_bytes = base64.b64decode(imagem_base64)
    gabarito = processar_imagem(imagem_bytes)
    dados = extrair_dados(gabarito)
    return dados
```

### Integração com Sistema de Arquivos

```python
import os
from datetime import datetime

def salvar_gabarito_processado(gabarito, qrcode):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    caminho = f'gabaritos_processados/{qrcode}_{timestamp}.png'
    
    os.makedirs('gabaritos_processados', exist_ok=True)
    cv2.imwrite(caminho, gabarito)
```

## Backup e Recuperação

### Backup de Resultados

```bash
# Backup diário
tar -czf backup_$(date +%Y%m%d).tar.gz results/
```

### Logs de Operação

```bash
# Monitorar logs em tempo real
tail -f app.log
```

## Segurança

### Validação de Entrada

```python
import imghdr

def validar_imagem(file_obj):
    file_obj.seek(0)
    tipo = imghdr.what(file_obj)
    file_obj.seek(0)
    return tipo in ('jpeg', 'png', 'bmp')

@app.route('/processar', methods=['POST'])
def processar():
    if not validar_imagem(request.files['imagem']):
        return {"erro": "Formato inválido"}, 400
```

### Limites de Taxa

```python
from flask_limiter import Limiter

limiter = Limiter(app)

@app.route('/processar', methods=['POST'])
@limiter.limit("10 per minute")
def processar():
    ...
```

### CORS (para clientes web)

```python
from flask_cors import CORS

CORS(app)
```

## Escalabilidade

### Processamento em Batch

```python
def processar_batch(arquivo_lista):
    resultados = []
    
    for arquivo in arquivo_lista:
        with open(arquivo, 'rb') as f:
            imagem_bytes = f.read()
        
        gabarito = processar_imagem(imagem_bytes)
        dados = extrair_dados(gabarito)
        resultados.append(dados)
    
    return resultados
```

### Paralelização com Multiprocessing

```python
from multiprocessing import Pool

def processar_unico(imagem_bytes):
    gabarito = processar_imagem(imagem_bytes)
    return extrair_dados(gabarito)

def processar_paralelo(lista_bytes, num_workers=4):
    with Pool(num_workers) as pool:
        return pool.map(processar_unico, lista_bytes)
```

## Referência Rápida de Comandos

| Tarefa | Comando |
|--------|---------|
| Instalar deps | `pip install -r requirements.txt` |
| Iniciar API | `python app.py` |
| Testar conectividade | `curl http://localhost:5000/health` |
| Testar processamento | `curl -X POST -F "imagem=@gabarito.png" http://localhost:5000/processar` |
| Rodar testes | `python teste.py` |
| Iniciar em produção | `gunicorn -w 4 app:app` |
| Ver logs | `tail -f app.log` |
| Parar servidor | `CTRL+C` |

