"""
Aplicação Flask para processamento de gabaritos de respostas.

Este módulo expõe uma API REST que recebe imagens de gabaritos de provas
objetivas, processa-as e retorna dados estruturados contendo:
- Identificação do respondente via QR code
- Alternativas selecionadas para cada questão

Módulos Dependentes:
    - image_processor: Processamento e normalização de imagens
    - data_extractor: Extração de QR code e alternativas

Endpoints:
    POST /processar: Processa imagem e retorna dados
    GET /health: Verifica estado da API

Uso:
    python app.py
"""

from flask import Flask, request, jsonify
from image_processor import processar_imagem
from data_extractor import extrair_dados


app = Flask(__name__)


@app.route('/processar', methods=['POST'])
def processar():
    """
    Endpoint principal para processamento de gabaritos.
    
    Recebe uma imagem binária de um gabarito, realiza todas as etapas de
    processamento e extração de dados, retornando um JSON com QR code e
    respostas detectadas.
    
    Requisição:
        POST /processar
        Content-Type: multipart/form-data
        Campo obrigatório: 'imagem' (arquivo binário JPEG/PNG)
    
    Exemplo com cURL:
        curl -X POST -F "imagem=@gabarito.png" http://localhost:5000/processar
    
    Resposta de Sucesso (HTTP 200):
        {
            "qrcode": "665f1a2b8c1234567890abcd",
            "respostas": {
                "1": "A",
                "2": "B",
                "3": null,
                "4": "D",
                "5": "E",
                "6": "A",
                "7": "B",
                "8": "C",
                "9": null,
                "10": "E"
            }
        }
    
    Resposta de Erro - Campo não enviado (HTTP 400):
        {
            "erro": "Nenhuma imagem enviada"
        }
    
    Resposta de Erro - Processamento falhou (HTTP 500):
        {
            "erro": "Mensagem descritiva da exceção"
        }
    
    Fluxo de Processamento:
        1. Validação: verifica presença do arquivo de imagem
        2. Leitura: lê bytes do arquivo em memória
        3. Normalização: processa imagem com image_processor.processar_imagem()
           - Detecta contorno do gabarito
           - Corrige perspectiva e ângulo
           - Normaliza para dimensões padrão (1200x286)
        4. Extração: extrai dados com data_extractor.extrair_dados()
           - Detecta e decodifica QR code
           - Identifica alternativas marcadas
           - Valida cada resposta
        5. Resposta: retorna JSON estruturado
    
    Returns:
        tuple: (dict com dados, código HTTP status)
    
    Raises:
        HTTP 400: Se nenhuma imagem foi fornecida
        HTTP 500: Se erro ocorrer durante processamento
    """
    try:
        # Validação: verifica se arquivo foi enviado
        if 'imagem' not in request.files:
            return jsonify({"erro": "Nenhuma imagem enviada"}), 400

        # Leitura: obtém arquivo e converte para bytes
        imagem_file = request.files['imagem']
        imagem_bytes = imagem_file.read()

        # Processamento: normaliza imagem (perspectiva + dimensões)
        gabarito = processar_imagem(imagem_bytes)
        
        # Extração: lê QR code e detecta alternativas
        dados = extrair_dados(gabarito)

        # Resposta de sucesso
        return jsonify(dados), 200

    except Exception as e:
        # Captura qualquer exceção durante processamento
        # Retorna mensagem de erro para debug
        return jsonify({"erro": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """
    Endpoint de verificação de saúde da API.
    
    Utilizado para verificar se a aplicação está operacional e respondendo.
    Não requer parâmetros. Útil para monitoramento e health checks.
    
    Requisição:
        GET /health
    
    Resposta (HTTP 200):
        {
            "status": "ok"
        }
    
    Returns:
        tuple: (dict com status, código HTTP 200)
    """
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    """
    Entrada principal da aplicação.
    
    Configuração:
        - debug=True: Modo desenvolvimento com auto-reload
        - host='0.0.0.0': Aceita conexões de qualquer interface de rede
        - port=5000: Porta padrão
    
    AVISO: Em produção, usar servidor WSGI como Gunicorn ou Waitress
    com debug=False.
    
    Para produção:
        gunicorn -w 4 -b 0.0.0.0:5000 app:app
    """
    app.run(debug=True, host='0.0.0.0', port=5000)
