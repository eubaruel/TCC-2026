from api.modelos.prova import Prova
from api.modelos.disciplina import Disciplina
from api.modelos.usuario import Usuario
from api.DAOs.prova_dao import Prova_dao

from api.utils.resposta_erro_http import resposta_erro_http

class Prova_service:
    def __init__(self, prova_dao_dependency: Prova_dao):
        print("⬆️ prova_service.__init__()")
        self.__prova_dao = prova_dao_dependency

    _CAMPOS_PROVA = [
        "id_turma",
        "status",
        "tipo",
        "serie",
        "bimestre",
        "data_de_aplicacao",
        "questoes"
    ]


    def criar (self, json_prova: dict):
        print("🟣 prova_service.criar()")

        obj_prova = Prova()
        self._setar_modelo_prova(obj_prova, json_prova)
        return self.__prova_dao.criar(obj_prova)
    

    def consulta(self, filtro) -> list[dict]:
        print("🟣 prova_service.consulta()")
        return self.__prova_dao.consulta(filtro)
    
    
    def atualizar(self, json_prova: dict, id_hash: str) -> bool:
        print("🟣 prova_service.atualizar()")

        obj_prova = Prova()
        self._setar_modelo_prova(obj_prova, json_prova)
        obj_prova.id_hash = id_hash

        if not self.__prova_dao.campo_existe("_id", obj_prova.id_hash):
            raise resposta_erro_http(
                400,
                "Prova não existe",
                {"mensagem":f'A prova com Id fornecido não existe no banco de dados'}
            )

        return self.__prova_dao.atualizar(obj_prova)
    

    def excluir(self, id_hash: str) -> bool:
        print("🟣 prova_service.excluir()")
        obj_prova = Prova()
        obj_prova.id_hash = id_hash
        return self.__prova_dao.excluir(obj_prova.id_hash)

    def _setar_modelo_prova(self,obj_prova,json_prova):
        for campo in self._CAMPOS_PROVA:
            setattr(obj_prova, campo, json_prova.get(campo))

        dados_professor = json_prova.get("professor")
        professor = Usuario()
        professor.nome = dados_professor.get("nome")
        obj_prova.professor = professor

        dados_disciplina = json_prova.get("disciplina")
        disciplina = Disciplina()
        disciplina.codigo_disciplina = dados_disciplina.get("codigo_disciplina")
        disciplina.nome_disciplina = dados_disciplina.get("nome_disciplina")
        obj_prova.disciplina = disciplina