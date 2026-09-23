# Sistema de Leitura Automática de Gabaritos

## Descrição Geral

Sistema de processamento de imagens e extração de dados para digitalização e análise automática de gabaritos de respostas (provas objetivas). O sistema utiliza visão computacional para detectar gabaritos em fotografias, corrigir perspectiva, normalizar dimensões, ler códigos QR e identificar as alternativas marcadas pelo respondente.

## Arquitetura

### Camadas

- **Camada de API**: Exposição de funcionalidades via HTTP REST (Flask)
- **Camada de Processamento de Imagem**: Detecção de contornos, correção de perspectiva e normalização
- **Camada de Extração de Dados**: Leitura de QR code e decodificação de alternativas marcadas
- **Camada de Testes**: Validação de performance e funcionalidade

### Fluxo de Processamento

```
Imagem Binária → Detecção de Gabarito → Correção de Perspectiva → Extração de QR Code
                                            ↓
                                   Detecção de Respostas → JSON Estruturado
```

## Módulos

### 1. app.py

Aplicação Flask que expõe a funcionalidade via HTTP REST.

#### Dependências
- Flask

#### Endpoints

##### POST /processar

Processa uma imagem de gabarito e retorna os dados extraídos.

**Requisição:**
- Method: POST
- Content-Type: multipart/form-data
- Campo obrigatório: `imagem` (arquivo binário)

**Resposta de Sucesso (200):**
```json
{
  "qrcode": "665f1a2b8c1234567890abcd",
  "respostas": {
    "1": "A",
    "2": "B",
    "3": "C",
    "4": null,
    "5": "D",
    "6": "E",
    "7": "A",
    "8": "B",
    "9": null,
    "10": "E"
  }
}
```

**Resposta de Erro (400):**
```json
{
  "erro": "Nenhuma imagem enviada"
}
```

**Resposta de Erro (500):**
```json
{
  "erro": "Mensagem de exceção"
}
```

**Fluxo de Processamento:**
1. Valida presença do arquivo de imagem
2. Lê bytes do arquivo
3. Chama `processar_imagem()` para normalizar e corrigir perspectiva
4. Chama `extrair_dados()` para obter QR code e alternativas
5. Retorna JSON estruturado

##### GET /health

Verifica estado operacional da API.

**Resposta (200):**
```json
{
  "status": "ok"
}
```

#### Configuração
- Debug: True (configurável para produção)
- Host: 0.0.0.0 (aceita conexões de qualquer origem)
- Porta: 5000

### 2. image_processor.py

Módulo de processamento de imagens para detecção, correção de perspectiva e normalização de gabaritos.

#### Dependências
- OpenCV (cv2)
- NumPy

#### Constantes Globais

| Constante | Valor | Descrição |
|-----------|-------|-----------|
| LARGURA_PADRAO | 1200 | Largura normalizada da imagem de saída (pixels) |
| ALTURA_PADRAO | 286 | Altura normalizada da imagem de saída (pixels) |

#### Funções

##### ordenar_pontos(pontos)

Ordena quatro pontos de um retângulo em ordem padrão (superior-esquerdo, superior-direito, inferior-direito, inferior-esquerdo).

**Entrada:**
- `pontos` (array-like): Coordenadas de 4 pontos [x, y]

**Saída:**
- `ndarray` (np.float32): Array 4x2 com pontos ordenados

**Algoritmo:**
- Calcula soma das coordenadas (identifica diagonal principal)
- Calcula diferença das coordenadas (identifica diagonal secundária)
- Ordena pontos baseado em argmin/argmax das operações

##### encontrar_gabarito(imagem)

Detecta o contorno retangular do gabarito na imagem através de análise de bordas e contornos.

**Entrada:**
- `imagem` (ndarray BGR): Imagem colorida em formato BGR

**Saída:**
- `ndarray` ou `None`: Array 4x2 com coordenadas dos 4 vértices do gabarito, ou None se não encontrado

**Critérios de Detecção:**
- Conversão para escala de cinza
- Detecção de bordas com Canny (thresholds: 50, 150)
- Operação morfológica de fechamento (kernel 7x7)
- Filtragem por área mínima (20% da área total da imagem)
- Aproximação poligonal com 4 vértices obrigatoriamente

**Retorno:**
- Contorno com maior área que atenda aos critérios
- None se nenhum contorno válido for encontrado

##### corrigir_perspectiva(imagem, pontos)

Corrige a perspectiva da imagem usando transformação homográfica a partir de 4 pontos conhecidos.

**Entrada:**
- `imagem` (ndarray BGR): Imagem original
- `pontos` (array-like): Coordenadas dos 4 vértices do gabarito

**Saída:**
- `ndarray` (BGR): Imagem com perspectiva corrigida e dimensões normalizadas

**Processo:**
- Ordena pontos através de `ordenar_pontos()`
- Define coordenadas destino (retângulo 1200x286 em pixels)
- Calcula matriz de transformação perspectiva (getPerspectiveTransform)
- Aplica transformação (warpPerspective)

##### processar_imagem(imagem_bytes)

Função principal que orquestra o processamento completo da imagem.

**Entrada:**
- `imagem_bytes` (bytes): Dados binários da imagem (JPEG, PNG, etc.)

**Saída:**
- `ndarray` (BGR): Imagem normalizada com dimensões LARGURA_PADRAO x ALTURA_PADRAO

**Lógica:**
- Decodifica bytes em array NumPy
- Decodifica imagem com imdecode (formato automático)
- Tenta encontrar gabarito na imagem
- Se encontrado: aplica correção de perspectiva
- Se não encontrado: faz resize simples

**Exceções:**
- ValueError: Se decodificação falhar

### 3. data_extractor.py

Módulo de extração de dados do gabarito normalizado (QR code e alternativas).

#### Dependências
- OpenCV (cv2)
- NumPy

#### Constantes Globais

| Constante | Valor | Descrição |
|-----------|-------|-----------|
| LARGURA_PADRAO | 1200 | Largura esperada da imagem (pixels) |
| ALTURA_PADRAO | 286 | Altura esperada da imagem (pixels) |
| ALTERNATIVAS | ["A", "B", "C", "D", "E"] | Mapeamento de índices para letras |

#### Constantes de Detecção

| Constante | Valor | Descrição |
|-----------|-------|-----------|
| LIMITE_MINIMO | 0.08 | Preenchimento mínimo para considerar resposta válida (8%) |
| DIFERENCA_MINIMA | 0.03 | Diferença mínima entre maior e segunda maior pontuação (3%) |

#### Funções

##### ler_qrcode(imagem)

Detecta e decodifica código QR na imagem.

**Entrada:**
- `imagem` (ndarray BGR): Imagem normalizada

**Saída:**
- `str` ou `None`: Conteúdo decodificado do QR code, ou None se não encontrado

**Método:**
- Utiliza cv2.QRCodeDetector nativo
- Não requer pré-processamento

##### detectar_respostas(imagem)

Detecta as 10 alternativas marcadas no gabarito através de análise de preenchimento.

**Entrada:**
- `imagem` (ndarray BGR): Imagem normalizada

**Saída:**
- `dict`: Dicionário com questões 1-10 como chaves, alternativas (A-E) ou None como valores

**Regiões de Interesse:**
- Extrai região contendo matriz de respostas (13.7% a 53.6% em largura, 40% a 88% em altura)
- Divide região em grid 10x5 (10 questões, 5 alternativas)

**Algoritmo de Detecção:**

Para cada questão (0-9):
1. Para cada alternativa (0-4):
   - Extrai célula individual do grid
   - Aplica margem de 25% em cada lado
   - Aplica threshold binário com OTSU
   - Calcula percentual de preenchimento (pixels pretos / total de pixels)
   
2. Obtém maior pontuação e respectiva alternativa
3. Valida resultado:
   - Maior pontuação >= LIMITE_MINIMO (0.08)
   - Diferença entre maior e segunda maior >= DIFERENCA_MINIMA (0.03)
   - Se válida: mapeia para letra (A-E)
   - Se inválida: marca como None (resposta em branco ou ambígua)

**Estrutura de Retorno:**
```python
{
  1: "A",      # Questão 1, resposta A
  2: "B",      # Questão 2, resposta B
  3: None,     # Questão 3, resposta não detectada
  ...
  10: "E"      # Questão 10, resposta E
}
```

##### extrair_dados(gabarito)

Função de orquestração que combina leitura de QR code e detecção de respostas.

**Entrada:**
- `gabarito` (ndarray BGR): Imagem normalizada do gabarito

**Saída:**
- `dict`: Estrutura com QR code e respostas

**Formato de Retorno:**
```python
{
  "qrcode": "665f1a2b8c1234567890abcd",  # ou "NÃO ENCONTRADO"
  "respostas": {
    "1": "A",
    "2": "B",
    ...
    "10": "E"
  }
}
```

### 4. teste.py

Script de teste de performance com dois modos de operação.

#### Dependências
- colorama
- requests
- concurrent.futures (stdlib)
- time (stdlib)

#### Configuração

| Parâmetro | Valor Padrão | Descrição |
|-----------|--------------|-----------|
| QUANTIDADE_REQUISICOES | 100 | Número de iterações de teste |
| ARQUIVO_IMAGEM | 'teste.png' | Arquivo de imagem para teste |
| URL_API | 'http://localhost:5000/processar' | Endpoint da API |
| MODO_TESTE | 'direto' | Tipo de teste: 'direto' ou 'api' |
| THREADS_PARALELAS | 8 | Número de threads paralelas (modo API) |

#### Modos de Teste

##### Modo Direto

Importa e executa funções sem overhead HTTP.

**Processo:**
- Lê arquivo de imagem uma vez
- Loop de 100 iterações chamando diretamente `processar_imagem()` e `extrair_dados()`
- Contabiliza sucessos e erros
- Metrifica tempo total

**Saída:**
- Tempo total em segundos
- Quantidade de sucessos/erros
- Tempo por correção em ms
- Taxa em gabaritos/segundo

##### Modo API

Executa requisições HTTP paralelas contra a API.

**Processo:**
- Lê arquivo de imagem uma vez
- Cria ThreadPoolExecutor com 8 workers
- Submete 100 requisições POST assíncronas
- Aguarda respostas e contabiliza sucessos (HTTP 200)
- Metrifica tempo total

**Saída:**
- Mesmo formato de resultados que modo direto
- Demonstra throughput com paralelismo

#### Fluxo de Execução

```
Carregamento de configuração
    ↓
Leitura de arquivo de imagem
    ↓
├─ Modo Direto: Loop sequencial
│   └─ Chamadas diretas de funções
│
└─ Modo API: Pool de threads
    └─ Requisições HTTP paralelas
    ↓
Metrificação de tempo e taxa de sucesso
    ↓
Exibição formatada de resultados
```

## Fluxo de Dados

### Entrada

```
Arquivo de imagem (JPEG, PNG)
        ↓
    Bytes
        ↓
[image_processor.processar_imagem()]
```

### Processamento

```
Imagem binária
    ↓
Conversão para escala de cinza
    ↓
Detecção de bordas (Canny)
    ↓
Operações morfológicas
    ↓
Detecção de contornos
    ↓
Filtragem por área
    ↓
Aproximação poligonal
    ↓
Ordenação de vértices
    ↓
Transformação perspectiva
    ↓
Normalização (1200x286)
```

### Extração

```
Imagem normalizada
    ├─ [ler_qrcode()] → String QR Code
    │
    └─ [detectar_respostas()]
        ├─ Conversão para cinza
        ├─ Extração de ROI (região de interesse)
        ├─ Divisão em grid 10x5
        ├─ Para cada célula:
        │   ├─ Aplicação de margem
        │   ├─ Threshold binário com OTSU
        │   └─ Cálculo de preenchimento
        ├─ Seleção de maior pontuação
        └─ Validação de limiares → Alternativa (A-E) ou None
```

### Saída

```json
{
  "qrcode": "string",
  "respostas": {
    "1": "A|B|C|D|E|null",
    "2": "A|B|C|D|E|null",
    ...
    "10": "A|B|C|D|E|null"
  }
}
```

## Parâmetros de Calibração

### Detecção de Gabarito (image_processor.py)

- **Thresholds Canny**: 50 (inferior), 150 (superior)
  - Aumentar: menos bordas detectadas, menos ruído
  - Diminuir: mais bordas detectadas, mais sensibilidade

- **Kernel Morfológico**: 7x7
  - Aumentar: mais fechamento de pequenas aberturas
  - Diminuir: mais detalhes preservados

- **Área Mínima**: 20% da imagem
  - Rejeita contornos menores que este limite
  - Ajustar se gabaritos forem muito pequenos na imagem

### Detecção de Respostas (data_extractor.py)

- **LIMITE_MINIMO**: 0.08 (8%)
  - Preenchimento mínimo para marcar resposta
  - Aumentar: rejeita marcas leves
  - Diminuir: aceita marcas mais tênues

- **DIFERENCA_MINIMA**: 0.03 (3%)
  - Diferença entre maior e segunda maior pontuação
  - Aumentar: rejeita respostas ambíguas
  - Diminuir: mais tolerante com ambiguidade

- **ROI (Region of Interest)**:
  - Largura: 13.7% a 53.6%
  - Altura: 40% a 88%
  - Ajustar se gabarito possui layout diferente

- **Margem de Célula**: 25%
  - Remove 25% das bordas de cada célula
  - Reduz influência de linhas do gabarito

## Requisitos do Sistema

### Dependências Python

- Flask >= 2.0
- opencv-python >= 4.5
- numpy >= 1.19
- colorama >= 0.4 (testes)
- requests >= 2.25 (testes)

### Requisitos de Hardware

- CPU com suporte a operações matriciais (recomendado)
- RAM: mínimo 512 MB
- Taxa de processamento esperada: ~0.5-2 segundos por gabarito (dependendo de CPU)

## Tratamento de Erros

### Em image_processor.py

| Condição | Exceção | Ação |
|----------|---------|------|
| Bytes inválidos | ValueError | Propaga ao chamador |
| Imagem não decodificável | Implícito (None) | Resize simples aplicado |
| Gabarito não detectado | Implícito (None) | Resize simples aplicado |

### Em app.py

| Condição | Status HTTP | Resposta |
|----------|-------------|----------|
| Imagem não enviada | 400 | `{"erro": "Nenhuma imagem enviada"}` |
| Erro de processamento | 500 | `{"erro": "mensagem de exceção"}` |

### Em data_extractor.py

| Condição | Retorno | Ação |
|----------|---------|------|
| QR code não encontrado | "NÃO ENCONTRADO" | Prossegue normalmente |
| Resposta inválida | None | Marcada como branco/indeciso |
| Célula vazia | 0 (pontuação) | Rejeitada automaticamente |

## Casos de Uso

### 1. Processamento Único

```python
from image_processor import processar_imagem
from data_extractor import extrair_dados

with open('gabarito.png', 'rb') as f:
    imagem_bytes = f.read()

gabarito_normalizado = processar_imagem(imagem_bytes)
resultado = extrair_dados(gabarito_normalizado)

print(resultado['qrcode'])      # ID do respondente
print(resultado['respostas'])   # Dicionário de respostas
```

### 2. Serviço Web

```bash
python app.py
# Servidor inicia em http://localhost:5000

# Em outro terminal
curl -X POST -F "imagem=@gabarito.png" http://localhost:5000/processar
```

### 3. Testes de Performance

```bash
# Teste direto (sem HTTP)
python teste.py

# Teste com API (alterar MODO_TESTE em teste.py)
MODO_TESTE='api'
python teste.py
```

## Limitações Conhecidas

1. **Tamanho de Imagem**: Otimizado para imagens de 640x480 ou superior. Imagens muito pequenas podem ter gabarito não detectado.

2. **Ângulos de Perspectiva**: Funciona bem com ângulos até ~45°. Ângulos maiores podem resultar em distorção excessiva.

3. **Iluminação**: Requer iluminação uniforme. Sombras fortes podem afetar detecção de preenchimento.

4. **Qualidade de Impressão**: Gabaritos impressos com baixa resolução ou desbotados podem gerar detecções incorretas.

5. **Layout Fixo**: Assume layout padrão do gabarito (10 questões, 5 alternativas). Layouts customizados requerem recalibração de constantes.

6. **Marcas Ambíguas**: Respostas parcialmente preenchidas ou com múltiplas marcas podem resultar em None.

## Métricas de Performance

### Modo Direto (sequencial)

- Processamento por gabarito: ~500-2000 ms (varia com resolução)
- Taxa média: ~1-2 gabaritos/segundo
- Uso de CPU: 1 core @ ~80-100%

### Modo API (8 threads)

- Taxa de throughput: ~3-5 gabaritos/segundo
- Latência por requisição: ~500-2000 ms
- Uso de CPU: múltiplos cores

## Exemplos de Resposta

### Sucesso Completo

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

### Com Respostas em Branco

```json
{
  "qrcode": "665f1a2b8c1234567890abcd",
  "respostas": {
    "1": "A",
    "2": null,
    "3": "C",
    "4": null,
    "5": "E",
    "6": "A",
    "7": null,
    "8": "C",
    "9": "D",
    "10": null
  }
}
```

### QR Code Não Encontrado

```json
{
  "qrcode": "NÃO ENCONTRADO",
  "respostas": {
    "1": "A",
    "2": "B",
    "3": "C",
    ...
  }
}
```

## Estrutura de Diretórios

```
.
├── app.py                  # API Flask
├── image_processor.py      # Processamento de imagem
├── data_extractor.py       # Extração de QR code e respostas
├── teste.py               # Script de testes
├── teste.png              # Imagem de teste (não incluído)
└── README.md              # Esta documentação
```

## Glossário

| Termo | Definição |
|-------|-----------|
| Gabarito | Formulário de resposta com matriz de alternativas |
| QR Code | Código bidimensional para identificação (armazena ID do respondente) |
| Perspectiva | Ângulo/inclinação da imagem capturada |
| ROI | Region of Interest - área de interesse específica da imagem |
| OTSU | Método automático de threshold binário baseado em histograma |
| Threshold | Valor limiar para conversão de imagem a preto e branco |
| Contorno | Traço/borda detectado em imagem binária |
| Kernel | Matriz de convolução para operações morfológicas |

