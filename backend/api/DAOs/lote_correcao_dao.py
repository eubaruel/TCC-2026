from bson import ObjectId


class Lote_correcao_dao:
    def __init__(self, banco_de_dados_dependency):
        self.__colecao = banco_de_dados_dependency.get_banco_de_dados()["lotes_correcao"]

    def criar(self, documento):
        documento = dict(documento)
        documento["_id"] = str(self.__colecao.insert_one(documento).inserted_id)
        return documento

    def buscar_por_id(self, id_lote):
        if not isinstance(id_lote, str) or not ObjectId.is_valid(id_lote):
            return None
        documento = self.__colecao.find_one({"_id": ObjectId(id_lote)})
        if documento:
            documento["_id"] = str(documento["_id"])
        return documento
