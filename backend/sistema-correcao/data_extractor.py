"""
Módulo de extração de dados de gabaritos normalizados.

Responsável pela leitura de QR code e detecção de alternativas marcadas
em gabaritos que já foram processados e normalizados.

Funções Principais:
    - extrair_dados(): Orquestração - extrai QR code e respostas
    - ler_qrcode(): Detecta e decodifica código QR
    - detectar_respostas(): Analisa matrix 10x5 e identifica marcas

Pipeline de Extração:
    Imagem Normalizada → QR Code Detection
                      → ROI Extraction (Region of Interest)
                      → Grid Division (10x5)
                      → Cell Analysis
                      → Validation
                      → Structured Output

Dependências:
    - cv2 (OpenCV): Processamento de imagem e QR code
    - numpy: Operações matriciais

Constantes:
    - LARGURA_PADRAO: Largura esperada (1200 pixels)
    - ALTURA_PADRAO: Altura esperada (286 pixels)
    - ALTERNATIVAS: Mapeamento índice → letra (A-E)
    - LIMITE_MINIMO: Preenchimento mínimo para validação
    - DIFERENCA_MINIMA: Diferença mínima entre respostas
"""

import cv2
import numpy as np


# ============================================================
# CONSTANTES GLOBAIS
# ============================================================

LARGURA_PADRAO = 1200
"""int: Largura esperada da imagem normalizada (pixels)."""

ALTURA_PADRAO = 286
"""int: Altura esperada da imagem normalizada (pixels)."""

ALTERNATIVAS = ["A", "B", "C", "D", "E"]
"""list: Mapeamento de índices (0-4) para letras de resposta."""


# ============================================================
# FUNÇÕES DE EXTRAÇÃO
# ============================================================

def ler_qrcode(imagem):
    """
    Detecta e decodifica código QR na imagem.
    
    Utiliza detector nativo do OpenCV (cv2.QRCodeDetector) para
    localizar padrões característicos de QR code e decodificar
    os dados armazenados.
    
    Processo:
        1. Localiza padrões de posicionamento (3 quadrados nos cantos)
        2. Detecta padrão de temporização e versão
        3. Decodifica dados usando algoritmo Reed-Solomon
    
    Args:
        imagem (np.ndarray): Imagem normalizada em formato BGR
            Esperado: (ALTURA_PADRAO, LARGURA_PADRAO, 3)
            Mas funciona com qualquer tamanho
    
    Returns:
        str or None:
            - Se QR code encontrado: string com dados decodificados
            - Se não encontrado: None
    
    Formatos Suportados:
        - QR code padrão ISO/IEC 18004
        - Versões 1-40
        - Capacidade: até 50 caracteres alfanuméricos
    
    Exemplo:
        >>> imagem = cv2.imread('gabarito.jpg')
        >>> qrcode_data = ler_qrcode(imagem)
        >>> if qrcode_data:
        ...     print(f"ID do respondente: {qrcode_data}")
        ... else:
        ...     print("QR code não encontrado")
    
    Notas:
        - Retorna None silenciosamente se não encontrado
        - Não requer pré-processamento da imagem
        - Função robusta a rotações e perspectivas
    """
    # Inicializa detector de QR code
    detector = cv2.QRCodeDetector()
    
    # Detecta e decodifica QR code
    # Retorna tupla: (dados, pontos_contorno, matriz_rotação)
    # Usa apenas o primeiro elemento (dados)
    resultado, _, _ = detector.detectAndDecode(imagem)
    
    # Retorna dados ou None
    return resultado if resultado else None


def detectar_respostas(imagem):
    """
    Detecta as 10 respostas do gabarito através de análise de preenchimento.
    
    Extrai a região contendo a matrix de respostas (10 questões x 5 alternativas),
    divide em células, analisa cada uma via threshold binário e conta pixels
    preenchidos, validando a resposta conforme limiares configurados.
    
    Estrutura Esperada:
        - Layout: 10 questões (colunas) × 5 alternativas (linhas)
        - ROI (Region of Interest): 13.7%-53.6% horizontal, 40%-88% vertical
        - Total de células: 50
        - Resposta válida: A, B, C, D, E ou None
    
    Processo por Célula:
        1. Extração: isola célula individual do grid
        2. Margem: aplica margem de 25% em todas direções
        3. Threshold: aplica binarização automática (Otsu)
        4. Análise: calcula percentual de pixels preenchidos
        5. Validação: verifica critérios de limite mínimo e diferença
    
    Critérios de Validação:
        - LIMITE_MINIMO (0.08): preenchimento >= 8%
        - DIFERENCA_MINIMA (0.03): diferença >= 3% entre maior/segunda maior
        - Se ambos forem satisfeitos: resposta é válida
        - Caso contrário: resposta é None (branco ou ambígua)
    
    Args:
        imagem (np.ndarray): Imagem normalizada em formato BGR
            Esperado: (ALTURA_PADRAO, LARGURA_PADRAO, 3)
            Deve estar corrigida de perspectiva
    
    Returns:
        dict: Dicionário com questões 1-10 como chaves
            Valores: letra (A-E) ou None
            
            Exemplo:
            {
                1: "A",
                2: "B",
                3: None,      # resposta em branco
                4: "D",
                5: "E",
                6: "A",
                7: "B",
                8: None,      # ambígua
                9: "D",
                10: "E"
            }
    
    Parametrização:
        - LIMITE_MINIMO: 0.08 (8% preenchimento mínimo)
        - DIFERENCA_MINIMA: 0.03 (3% diferença mínima)
        - Margem de célula: 25%
        - Threshold: Otsu automático
        - ROI X: 13.7% a 53.6%
        - ROI Y: 40% a 88%
    
    Exemplo:
        >>> imagem = cv2.imread('gabarito_normalizado.jpg')
        >>> respostas = detectar_respostas(imagem)
        >>> print(f"Questão 1: {respostas[1]}")
        Questão 1: A
    """
    # Conversão BGR → Escala de Cinza
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    # Extração de Região de Interesse (ROI)
    # Coordenadas calculadas como percentual das dimensões padrão
    x_inicio = int(LARGURA_PADRAO * 0.137)   # 164 pixels
    x_fim = int(LARGURA_PADRAO * 0.536)      # 643 pixels
    y_inicio = int(ALTURA_PADRAO * 0.40)     # 114 pixels
    y_fim = int(ALTURA_PADRAO * 0.88)        # 252 pixels

    # Extrai submatriz contendo apenas a grid de respostas
    # Dimensões: ~479 × 138 pixels
    matriz = cinza[y_inicio:y_fim, x_inicio:x_fim]

    # Cálculo de dimensões da célula
    altura, largura = matriz.shape
    largura_coluna = largura / 10    # ~47.9 pixels
    altura_linha = altura / 5        # ~27.6 pixels

    # Dicionário para armazenar respostas detectadas
    respostas = {}

    # Limiares de validação
    LIMITE_MINIMO = 0.08        # Preenchimento mínimo (8%)
    DIFERENCA_MINIMA = 0.03     # Diferença mínima entre maior/segunda (3%)

    # Loop: uma iteração por questão (0-9)
    for questao in range(10):
        # Lista para armazenar pontuações de cada alternativa
        pontuacoes = []

        # Loop interno: uma iteração por alternativa (0-4: A-E)
        for alternativa in range(5):
            # Cálculo de coordenadas da célula
            x1 = int(questao * largura_coluna)
            x2 = int((questao + 1) * largura_coluna)
            y1 = int(alternativa * altura_linha)
            y2 = int((alternativa + 1) * altura_linha)

            # Aplicação de margem (25% em cada lado)
            # Remove influência das linhas de grid
            margem_x = int((x2 - x1) * 0.25)
            margem_y = int((y2 - y1) * 0.25)

            x1 += margem_x
            x2 -= margem_x
            y1 += margem_y
            y2 -= margem_y

            # Extração da célula
            celula = matriz[y1:y2, x1:x2]

            # Validação: célula vazia ou inválida
            if celula.size == 0:
                pontuacoes.append(0)
                continue

            # Threshold Binário com OTSU
            # THRESH_BINARY_INV: inverte (marca = branco)
            # THRESH_OTSU: calcula limiar automaticamente
            _, binaria = cv2.threshold(
                celula,
                0,
                255,
                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )

            # Análise: conta pixels brancos (preenchidos)
            # countNonZero: retorna número de pixels não-zero
            # Preenchimento = pixels_brancos / pixels_totais
            preenchimento = cv2.countNonZero(binaria) / binaria.size
            pontuacoes.append(preenchimento)

        # Análise de pontuações
        # Encontra maior e segunda maior pontuação
        maior = max(pontuacoes)
        indice = pontuacoes.index(maior)
        ordenadas = sorted(pontuacoes, reverse=True)
        segunda_maior = ordenadas[1]

        # Validação de Resposta
        # Dois critérios devem ser atendidos:
        # 1. Preenchimento mínimo (>= 8%)
        # 2. Diferença clara (>= 3%) entre maior e segunda maior
        if maior < LIMITE_MINIMO or maior - segunda_maior < DIFERENCA_MINIMA:
            # Falha em algum critério: resposta inválida
            # Pode ser: marca muito leve, múltiplas marcas, ou branco
            respostas[questao + 1] = None
        else:
            # Ambos critérios atendidos: resposta válida
            # Mapeia índice (0-4) para letra (A-E)
            respostas[questao + 1] = ALTERNATIVAS[indice]

    return respostas


def extrair_dados(gabarito):
    """
    Extrai todos os dados do gabarito normalizado.
    
    Função de orquestração que chama as subfunções para extrair:
    - QR code: identificação do respondente
    - Respostas: alternativas selecionadas (10 questões)
    
    E retorna estrutura unificada para processamento posterior.
    
    Args:
        gabarito (np.ndarray): Imagem normalizada em formato BGR
            Esperado: (ALTURA_PADRAO, LARGURA_PADRAO, 3)
            Deve estar corrigida de perspectiva (de processar_imagem())
    
    Returns:
        dict: Estrutura com QR code e respostas
            
            Formato:
            {
                "qrcode": "665f1a2b8c1234567890abcd" ou "NÃO ENCONTRADO",
                "respostas": {
                    "1": "A" ou null,
                    "2": "B" ou null,
                    ...
                    "10": "E" ou null
                }
            }
    
    Exemplo de Retorno (Sucesso Completo):
        {
            "qrcode": "ID123456789",
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
    
    Exemplo de Retorno (QR Não Encontrado):
        {
            "qrcode": "NÃO ENCONTRADO",
            "respostas": {
                "1": "A",
                ...
                "10": "E"
            }
        }
    
    Exemplo de Retorno (Com Respostas em Branco):
        {
            "qrcode": "ID123456789",
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
    
    Fluxo:
        1. Chama ler_qrcode() para detectar ID
        2. Chama detectar_respostas() para extrair alternativas
        3. Combina resultados em estrutura única
        4. Retorna JSON-ready dict
    
    Notas:
        - QR code não encontrado: string "NÃO ENCONTRADO"
        - Resposta ambígua/branca: null (None em Python)
        - Função nunca levanta exceção (trata erros internamente)
    """
    # Leitura do QR code
    qrcode = ler_qrcode(gabarito)
    
    # Detecção das respostas (10 questões)
    respostas = detectar_respostas(gabarito)

    # Montagem da estrutura de retorno
    return {
        "qrcode": qrcode if qrcode else "NÃO ENCONTRADO",
        "respostas": respostas
    }
