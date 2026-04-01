from pymongo import MongoClient
import sys

class Database:

    __client = None

    def __init__(self, uri="***REMOVIDO***", db_name="tcc2026"):
        self.uri = uri
        self.db_name = db_name

    def connect(self):
        if Database.__client is None:
            try:
                Database.__client = MongoClient(self.uri)

                # Teste de conexão
                Database.__client.admin.command('ping')

                print("⬆️ Conectado ao MongoDB com sucesso!")

            except Exception as error:
                print(f"❌ Falha ao conectar ao MongoDB: {error}")
                sys.exit(1)

        return Database.__client

    def get_database(self):
        client = self.connect()
        return client[self.db_name]



