"""
Script de teste de performance do sistema de leitura de gabaritos.

Fornece dois modos de teste:
    1. Direto: Chamadas sequenciais de funções sem overhead HTTP
    2. API: Requisições HTTP paralelas contra servidor Flask

Útil para:
    - Validação de funcionalidade
    - Medição de performance (latência, throughput)
    - Identificação de gargalos
    - Comparação direto vs HTTP

Configuração:
    Edite constantes QUANTIDADE_REQUISICOES, ARQUIVO_IMAGEM, etc.
    no início do script.

Dependências:
    - colorama: Formatação de cores no terminal
    - requests: Cliente HTTP (modo API apenas)
    - concurrent.futures: Paralelização (modo API)
    - image_processor, data_extractor: (modo direto)

Uso:
    # Modo Direto (sequencial)
    python teste.py
    
    # Modo API (paralelo)
    # 1. Alterar MODO_TESTE = 'api' no script
    # 2. python app.py (em outro terminal)
    # 3. python teste.py
"""

import time
from colorama import Fore, Back, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests


# Inicializa colorama (necessário para cores em Windows)
init(autoreset=True)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

QUANTIDADE_REQUISICOES = 100
"""int: Número de iterações de teste."""

ARQUIVO_IMAGEM = 'teste.png'
"""str: Caminho do arquivo de imagem para teste."""

URL_API = 'http://localhost:5000/processar'
"""str: URL do endpoint de processamento (modo API)."""

MODO_TESTE = 'direto'
"""str: Modo de teste - 'direto' ou 'api'."""

THREADS_PARALELAS = 8
"""int: Número de threads paralelas (usado em modo API)."""


# ============================================================
# TESTE DIRETO (SEM HTTP - MAIS RÁPIDO)
# ============================================================

if MODO_TESTE == 'direto':
    """
    Modo Teste Direto
    
    Importa e executa funções de processamento diretamente,
    sem overhead de HTTP. Ideal para baseline de performance
    e validação de funcionalidade básica.
    
    Processo:
        1. Carrega arquivo de imagem uma única vez em memória
        2. Loop de N iterações
        3. Cada iteração:
           - Chama processar_imagem() com bytes
           - Chama extrair_dados() com imagem normalizada
           - Contabiliza sucesso/erro
        4. Metrifica tempo total
    
    Saída:
        - Estatísticas de sucesso/erro
        - Tempo total de execução
        - Taxa de processamento (gabaritos/segundo)
        - Tempo por gabarito
    """
    
    # Importação de funções de processamento
    from image_processor import processar_imagem
    from data_extractor import extrair_dados

    # Exibição de cabeçalho
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}  TESTE DIRETO - SEM HTTP")
    print(f"{Fore.CYAN}{'='*60}\n")

    # Exibição de configuração
    print(f"{Fore.YELLOW}📊 Configuração:")
    print(f"{Fore.WHITE}   • Requisições: {Fore.GREEN}{QUANTIDADE_REQUISICOES}")
    print(f"{Fore.WHITE}   • Arquivo: {Fore.GREEN}{ARQUIVO_IMAGEM}")
    print(f"{Fore.WHITE}   • Modo: {Fore.MAGENTA}Direto (sem HTTP)\n")

    # Carregamento de arquivo de imagem (uma única vez)
    with open(ARQUIVO_IMAGEM, 'rb') as f:
        imagem_bytes = f.read()

    # Inicialização de contadores
    tempo_inicio = time.time()
    sucessos = 0
    erros = 0

    print(f"{Fore.YELLOW}🚀 Iniciando testes...\n")

    # Loop principal: N iterações de processamento
    for i in range(1, QUANTIDADE_REQUISICOES + 1):
        try:
            # Etapa 1: Processamento de imagem (normalização + perspectiva)
            gabarito = processar_imagem(imagem_bytes)
            
            # Etapa 2: Extração de dados (QR code + respostas)
            dados = extrair_dados(gabarito)
            
            # Contabilização
            sucessos += 1
            
            # Feedback a cada 10 iterações
            if i % 10 == 0:
                print(f"{Fore.GREEN}✓ {i}/{QUANTIDADE_REQUISICOES}")
        
        except Exception as e:
            # Tratamento de erro
            erros += 1
            print(f"{Fore.RED}✗ {i}/{QUANTIDADE_REQUISICOES} - Erro: {e}")

    # Cálculo de tempo total
    tempo_total = time.time() - tempo_inicio


# ============================================================
# TESTE VIA API (COM HTTP)
# ============================================================

else:
    """
    Modo Teste API
    
    Executa requisições HTTP paralelas contra servidor Flask.
    Simula múltiplos clientes enviando gabaritos simultaneamente.
    Ideal para teste de carga, throughput e estabilidade.
    
    Processo:
        1. Carrega arquivo de imagem uma única vez
        2. ThreadPoolExecutor com N workers
        3. Para cada requisição:
           - Envia POST com arquivo via multipart/form-data
           - Aguarda resposta
           - Contabiliza sucesso (status 200) ou erro
        4. Metrifica tempo total e taxa de throughput
    
    Saída:
        - Estatísticas de sucesso/erro (paralelo)
        - Tempo total (inclui overhead HTTP)
        - Taxa de throughput (requisições/segundo)
        - Latência aparente por requisição
    
    Nota: Tempo por requisição inclui latência HTTP/rede
    """
    
    # Exibição de cabeçalho
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}  TESTE API - COM HTTP (PARALELO)")
    print(f"{Fore.CYAN}{'='*60}\n")

    # Exibição de configuração
    print(f"{Fore.YELLOW}📊 Configuração:")
    print(f"{Fore.WHITE}   • Requisições: {Fore.GREEN}{QUANTIDADE_REQUISICOES}")
    print(f"{Fore.WHITE}   • Threads paralelas: {Fore.GREEN}{THREADS_PARALELAS}")
    print(f"{Fore.WHITE}   • URL: {Fore.GREEN}{URL_API}\n")

    # Carregamento de arquivo de imagem (uma única vez)
    with open(ARQUIVO_IMAGEM, 'rb') as f:
        imagem_bytes = f.read()

    # Função auxiliar: executa uma requisição POST
    def fazer_requisicao(numero):
        """
        Envia uma requisição HTTP POST ao endpoint de processamento.
        
        Args:
            numero (int): Identificador da requisição (para logging)
        
        Returns:
            bool: True se status HTTP 200, False caso contrário
        """
        try:
            # Preparação de payload multipart
            files = {'imagem': (ARQUIVO_IMAGEM, imagem_bytes)}
            
            # Envio de requisição com timeout de 10 segundos
            response = requests.post(URL_API, files=files, timeout=10)
            
            # Retorna True se sucesso (status 200)
            return response.status_code == 200
        
        except:
            # Qualquer erro (conexão, timeout, etc): retorna False
            return False

    # Inicialização de contadores
    tempo_inicio = time.time()
    sucessos = 0

    print(f"{Fore.YELLOW}🚀 Iniciando requisições paralelas...\n")

    # Execução paralela com ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=THREADS_PARALELAS) as executor:
        # Submissão de todas as requisições
        futures = [
            executor.submit(fazer_requisicao, i) 
            for i in range(1, QUANTIDADE_REQUISICOES + 1)
        ]
        
        # Processamento de resultados conforme completam
        for i, future in enumerate(as_completed(futures), 1):
            # Se requisição foi bem-sucedida
            if future.result():
                sucessos += 1
            
            # Feedback a cada 10 requisições
            if i % 10 == 0:
                print(f"{Fore.GREEN}✓ {i}/{QUANTIDADE_REQUISICOES}")

    # Cálculo de tempo total
    tempo_total = time.time() - tempo_inicio
    
    # Cálculo de erros
    erros = QUANTIDADE_REQUISICOES - sucessos


# ============================================================
# RESULTADOS (COMUM PARA AMBOS MODOS)
# ============================================================

"""
Seção de Relatório

Exibe estatísticas consolidadas de performance:
- Tempo de execução total
- Taxa de sucesso/falha
- Latência por requisição
- Throughput (requisições/segundo)
"""

print(f"\n{Fore.CYAN}{'='*60}")
print(f"{Fore.CYAN}  RESULTADOS")
print(f"{Fore.CYAN}{'='*60}\n")

# Exibição de resultados básicos
print(f"{Fore.WHITE}Tempo total: {Fore.YELLOW}{tempo_total:.2f}s")
print(f"{Fore.WHITE}Sucessos: {Fore.GREEN}{sucessos}")
print(f"{Fore.WHITE}Erros: {Fore.RED}{erros}")

# Cálculo e exibição de métricas derivadas
if sucessos > 0:
    # Tempo por requisição bem-sucedida (em ms)
    tempo_por_requisicao = tempo_total / sucessos
    
    # Taxa de throughput (requisições/segundo)
    requisicoes_por_segundo = sucessos / tempo_total
    
    # Exibição de métricas
    print(f"\n{Fore.WHITE}Tempo por correção: {Fore.YELLOW}{tempo_por_requisicao*1000:.2f}ms")
    print(f"{Fore.WHITE}Correções por segundo: {Fore.GREEN}{requisicoes_por_segundo:.2f} req/s")
    
    # Exibição de destaque (resumo executivo)
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.GREEN}{Back.BLACK}  ✨ PERFORMANCE: {requisicoes_por_segundo:.2f} gabaritos/segundo  ✨")
    print(f"{Fore.CYAN}{'='*60}\n")
