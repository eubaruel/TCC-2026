from pymongo import MongoClient
import sys

class Banco_de_dados:

    __client = None

    def __init__(self, uri="uri_do_banco", nome_bd="nome_do_banco"):
        self.uri = uri
        self.nome_bd = nome_bd

    def conectar(self):
        if Banco_de_dados.__client is None:
            try:
                Banco_de_dados.__client = MongoClient(self.uri)

                # Teste de conexão
                Banco_de_dados.__client.admin.command('ping')

                print("⬆️ Conectado ao MongoDB com sucesso!")

            except Exception as error:
                print(f"❌ Falha ao conectar ao MongoDB: {error}")
                sys.exit(1)

        return Banco_de_dados.__client

    def get_banco_de_dados(self):
        client = self.conectar()
        return client[self.nome_bd]

    def fechar_conexao(self):
        try: 
            if Banco_de_dados.__client:
                Banco_de_dados.__client.close()
        except Exception:
            print("Banco de dados não conectado")



