import pymongo
cliente = pymongo.MongoClient("***REMOVIDO***")
banco_de_dados = cliente["tcc2026"]
questao = banco_de_dados['questao']
