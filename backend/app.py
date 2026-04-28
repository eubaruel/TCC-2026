import os
from dotenv import load_dotenv

load_dotenv()

from servidor import Servidor

"""
Arquivo principal de inicialização do servidor Flask.

Responsabilidades:
- Cria a instância do servidor
- Inicializa todas as dependências (banco, middlewares, rotas)
- Inicia o servidor na porta especificada
"""

def main():
    try:
        # Cria instância do servidor na porta fornecida pela .env
        servidor = Servidor(porta=int(os.getenv("PORTA",8080)))

        # Inicializa servidor (DB, middlewares, roteadores)
        servidor.init()

        # Inicia servidor Flask
        servidor.run()
        
        # Fecha a conexão com o banco de dados após encerrar o servidor
        servidor.close()
    except Exception as error:
        print("❌ Erro ao iniciar o servidor:", error)

main()