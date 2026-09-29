"""
Módulo de processamento e normalização de imagens de gabaritos.

Responsável pelo pipeline de visão computacional para detectar gabaritos
em fotografias, corrigir perspectiva e normalizar para dimensões padrão.

Pipeline de Processamento:
    Bytes → Decodificação → Detecção de Gabarito → Correção de Perspectiva
    → Imagem Normalizada (1200x286)

Funções Principais:
    - processar_imagem(): Função de orquestração principal
    - encontrar_gabarito(): Detecta contorno do gabarito
    - corrigir_perspectiva(): Aplica transformação homográfica
    - ordenar_pontos(): Ordena vértices em sequência padrão

Dependências:
    - cv2 (OpenCV): Processamento de imagem
    - numpy: Operações matriciais

Constantes:
    - LARGURA_PADRAO: Largura normalizada (1200 pixels)
    - ALTURA_PADRAO: Altura normalizada (286 pixels)
"""

import cv2
import numpy as np


# ============================================================
# CONSTANTES GLOBAIS
# ============================================================

LARGURA_PADRAO = 1200
"""int: Largura normalizada da imagem de saída em pixels."""

ALTURA_PADRAO = 286
"""int: Altura normalizada da imagem de saída em pixels."""


# ============================================================
# FUNÇÕES DE PROCESSAMENTO
# ============================================================

def ordenar_pontos(pontos):
    """
    Ordena 4 pontos de um quadrilátero em sequência padrão.
    
    Converte uma lista desordenada de 4 pontos (vértices de um quadrilátero)
    para a ordem padrão: superior-esquerdo, superior-direito, inferior-direito,
    inferior-esquerdo. Esta ordenação é necessária para a transformação
    de perspectiva correta.
    
    Algoritmo:
        1. Calcula soma das coordenadas (x + y)
           - Menor soma = canto superior-esquerdo
           - Maior soma = canto inferior-direito
        2. Calcula diferença das coordenadas (x - y)
           - Menor diferença = canto inferior-esquerdo
           - Maior diferença = canto superior-direito
    
    Args:
        pontos (array-like): Coordenadas dos 4 pontos em formato [x, y]
            Pode ser lista, tuple, ou array numpy
            Ordem arbitrária
    
    Returns:
        np.ndarray: Array 4x2 dtype float32 com pontos ordenados como:
            [[x_sup_esq, y_sup_esq],      # superior-esquerdo
             [x_sup_dir, y_sup_dir],      # superior-direito
             [x_inf_dir, y_inf_dir],      # inferior-direito
             [x_inf_esq, y_inf_esq]]      # inferior-esquerdo
    
    Exemplo:
        >>> pontos = [[100, 200], [400, 100], [500, 500], [200, 400]]
        >>> ordenados = ordenar_pontos(pontos)
        >>> print(ordenados.shape)
        (4, 2)
    """
    # Converte para array numpy float32 (compatível com OpenCV)
    pontos = np.array(pontos, dtype=np.float32)
    
    # Calcula soma das coordenadas (x + y)
    # Para diagonal principal: menor soma = topo-esquerdo, maior = fundo-direito
    soma = pontos.sum(axis=1)
    
    # Calcula diferença das coordenadas (x - y)
    # Para diagonal secundária: menor dif = fundo-esquerdo, maior = topo-direito
    diferenca = np.diff(pontos, axis=1).flatten()

    # Identifica cada vértice pelos extremos
    superior_esquerdo = pontos[np.argmin(soma)]
    inferior_direito = pontos[np.argmax(soma)]
    superior_direito = pontos[np.argmin(diferenca)]
    inferior_esquerdo = pontos[np.argmax(diferenca)]

    # Retorna pontos em ordem padrão
    return np.array([
        superior_esquerdo,
        superior_direito,
        inferior_direito,
        inferior_esquerdo
    ], dtype=np.float32)


def encontrar_gabarito(imagem):
    """
    Detecta o contorno retangular do gabarito na imagem.
    
    Utiliza pipeline de visão computacional para identificar o gabarito:
        1. Conversão para escala de cinza
        2. Detecção de bordas com algoritmo Canny
        3. Operações morfológicas (fechamento) para preenchimento
        4. Detecção de contornos
        5. Filtragem por critérios (área, forma)
        6. Seleção do melhor contorno
    
    Critérios de Válidade:
        - Área >= 20% da imagem (rejeita objetos pequenos)
        - Aproximação poligonal com exatamente 4 vértices
        - Maior área entre candidatos válidos
    
    Args:
        imagem (np.ndarray): Imagem colorida em formato BGR
            Dimensões: (altura, largura, 3 canais)
            Tipo: uint8 (0-255 por canal)
    
    Returns:
        np.ndarray or None: 
            - Se encontrado: array 4x2 com coordenadas dos vértices
            - Se não encontrado: None
        
        Array de retorno (se válido):
            [[x1, y1],   # vértice 1
             [x2, y2],   # vértice 2
             [x3, y3],   # vértice 3
             [x4, y4]]   # vértice 4
    
    Parâmetros de Ajuste (dentro da função):
        - Canny thresholds: 50 (baixo), 150 (alto)
        - Kernel morfológico: 7x7
        - Área mínima: 20% da imagem
        - Epsilon poligonal: 2% do perímetro
    
    Exemplo:
        >>> imagem = cv2.imread('foto_gabarito.jpg')
        >>> pontos = encontrar_gabarito(imagem)
        >>> if pontos is not None:
        ...     print(f"Gabarito encontrado em: {pontos}")
    """
    # Conversão BGR → Escala de Cinza
    # Reduz 3 canais a 1, mantendo informação de luminância
    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    # Detecção de Bordas - Algoritmo Canny
    # Thresholds: 50 (baixo) e 150 (alto)
    # Razão 1:3 recomendada para bom contraste
    bordas = cv2.Canny(cinza, 50, 150)

    # Operação Morfológica - Fechamento (Closing)
    # Preenche pequenos buracos em objetos (ex: furos dentro do gabarito)
    # Kernel retangular 7x7: suaviza contornos
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    bordas = cv2.morphologyEx(bordas, cv2.MORPH_CLOSE, kernel)

    # Detecção de Contornos
    # RETR_EXTERNAL: encontra apenas contornos externos (não hierarquias)
    # CHAIN_APPROX_SIMPLE: comprime contornos (remove pontos colineares)
    contornos, _ = cv2.findContours(
        bordas,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # Cálculo da área mínima (20% da imagem)
    # Rejeita contornos muito pequenos que não podem ser gabaritos
    altura, largura = cinza.shape
    area_imagem = largura * altura
    
    melhor = None
    melhor_area = 0

    # Iteração sobre todos os contornos encontrados
    for contorno in contornos:
        area = cv2.contourArea(contorno)

        # Filtro 1: Área mínima
        # Se menor que 20% da imagem, não pode ser gabarito
        if area < area_imagem * 0.20:
            continue

        # Aproximação Poligonal - Algoritmo Ramer-Douglas-Peucker
        # Epsilon = 2% do perímetro (precisão da aproximação)
        # Reduz número de vértices do contorno
        perimetro = cv2.arcLength(contorno, True)
        aproximacao = cv2.approxPolyDP(contorno, 0.02 * perimetro, True)

        # Filtro 2: Exatamente 4 vértices
        # Gabarito deve ser quadrilátero (4 lados)
        if len(aproximacao) != 4:
            continue

        # Seleção do melhor candidato
        # Entre os contornos válidos, escolhe o de maior área
        if area > melhor_area:
            melhor = aproximacao.reshape(4, 2)
            melhor_area = area

    # Retorna melhor contorno encontrado ou None
    return melhor


def corrigir_perspectiva(imagem, pontos):
    """
    Corrige a perspectiva de uma imagem usando transformação homográfica.
    
    Aplica transformação de perspectiva para converter um quadrilátero
    inclinado em um retângulo normalizado (1200x286 pixels). Útil para
    corrigir fotos de gabaritos tiradas em ângulo.
    
    Processo:
        1. Ordena os 4 pontos em sequência padrão
        2. Define coordenadas de destino (retângulo normalizado)
        3. Calcula matriz de transformação perspectiva (homografia)
        4. Aplica transformação à imagem original
    
    Args:
        imagem (np.ndarray): Imagem original em formato BGR
            Qualquer tamanho
        pontos (array-like): Coordenadas dos 4 vértices do quadrilátero
            Formato: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
            Ordem: arbitrária (será reordenada internamente)
    
    Returns:
        np.ndarray: Imagem com perspectiva corrigida
            Dimensões: (ALTURA_PADRAO, LARGURA_PADRAO, 3) = (286, 1200, 3)
            Tipo: uint8 (BGR)
            Interpolação: Bilinear
    
    Matemática:
        Transformação homográfica 3x3 que mapeia:
        [x', y', w'] = H @ [x, y, 1]
        
        Coordenadas finais: (x'/w', y'/w')
    
    Parâmetros Internos:
        - Coordenadas de destino: retângulo 0,0 a 1199,285
        - Interpolação: cv2.INTER_LINEAR (Bilinear)
    
    Exemplo:
        >>> imagem = cv2.imread('gabarito_inclinado.jpg')
        >>> pontos = [[100, 150], [400, 120], [420, 320], [80, 350]]
        >>> corrigida = corrigir_perspectiva(imagem, pontos)
        >>> print(corrigida.shape)
        (286, 1200, 3)
    """
    # Ordena pontos em sequência padrão
    # Garante que a transformação funcione corretamente
    pontos = ordenar_pontos(pontos)

    # Define coordenadas de destino
    # Retângulo normalizado com dimensões LARGURA_PADRAO x ALTURA_PADRAO
    # -1 garante que a indexação fica em 0 a LARGURA_PADRAO-1
    destino = np.array([
        [0, 0],
        [LARGURA_PADRAO - 1, 0],
        [LARGURA_PADRAO - 1, ALTURA_PADRAO - 1],
        [0, ALTURA_PADRAO - 1]
    ], dtype=np.float32)

    # Calcula matriz de transformação perspectiva
    # getPerspectiveTransform calcula matriz H (3x3)
    # que mapeia pontos origem para pontos destino
    matriz = cv2.getPerspectiveTransform(pontos, destino)
    
    # Aplica transformação à imagem
    # warpPerspective reamostra pixels usando interpolação bilinear
    corrigida = cv2.warpPerspective(
        imagem,
        matriz,
        (LARGURA_PADRAO, ALTURA_PADRAO)
    )

    return corrigida


def processar_imagem(imagem_bytes):
    """
    Função principal de orquestração do processamento de imagem.
    
    Encadeia todas as etapas do pipeline:
        1. Decodificação: bytes → imagem BGR
        2. Detecção: encontra contorno do gabarito
        3. Transformação: corrige perspectiva
        4. Normalização: padroniza dimensões
    
    Modo de Fallback:
        Se o gabarito não for detectado, aplica redimensionamento
        simples (preserva conteúdo, mas pode resultar em distorção
        se a foto foi tirada em ângulo)
    
    Args:
        imagem_bytes (bytes): Dados binários da imagem
            Formatos suportados: JPEG, PNG, BMP, etc.
            Qualquer tamanho/resolução
    
    Returns:
        np.ndarray: Imagem processada pronta para extração de dados
            Dimensões: (ALTURA_PADRAO, LARGURA_PADRAO, 3) = (286, 1200, 3)
            Tipo: uint8 (BGR)
    
    Raises:
        ValueError: Se a decodificação da imagem falhar
            Causas: arquivo corrompido, formato inválido
    
    Fluxo de Sucesso:
        bytes → imdecode → encontrar_gabarito (OK) 
        → corrigir_perspectiva → [1200x286]
    
    Fluxo de Fallback:
        bytes → imdecode → encontrar_gabarito (None) 
        → resize simples → [1200x286]
    
    Exemplo:
        >>> with open('gabarito.jpg', 'rb') as f:
        ...     imagem_bytes = f.read()
        >>> gabarito_normalizado = processar_imagem(imagem_bytes)
        >>> print(gabarito_normalizado.shape)
        (286, 1200, 3)
    """
    # Decodificação de Bytes → NumPy Array
    # frombuffer: converte bytes para array NumPy
    # uint8: tipo numérico (bytes são 0-255)
    nparr = np.frombuffer(imagem_bytes, np.uint8)
    
    # Decodificação de Array → Imagem
    # imdecode: decodifica formatos comprimidos (JPEG, PNG)
    # IMREAD_COLOR: retorna imagem colorida (BGR)
    # Se falhar, retorna None
    imagem = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Validação: imagem foi decodificada corretamente
    if imagem is None:
        raise ValueError("Erro ao decodificar imagem")

    # Tentativa de detectar gabarito (perspectivado)
    pontos = encontrar_gabarito(imagem)

    # Condicional: usar transformação perspectiva ou fallback
    if pontos is None:
        # Fallback: gabarito não detectado
        # Aplicar resize simples (pode resultar em distorção)
        gabarito = cv2.resize(imagem, (LARGURA_PADRAO, ALTURA_PADRAO))
    else:
        # Sucesso: gabarito detectado
        # Aplicar correção de perspectiva
        gabarito = corrigir_perspectiva(imagem, pontos)

    return gabarito
