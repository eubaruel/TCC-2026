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
        # Cria instância do servidor na porta 8080
        servidor = Servidor(porta=8080)

        # Inicializa servidor (DB, middlewares, roteadores)
        servidor.init()

        # Inicia servidor Flask
        servidor.run()

        print("✅ Servidor iniciado com sucesso")
    except Exception as error:
        print("❌ Erro ao iniciar o servidor:", error)

main()