from api.modelos.questao import Questao
from api.modelos.usuario import Usuario
from api.DAOs.questao_dao import Questao_dao

from api.utils.resposta_erro_http import resposta_erro_http

class Questao_service:
    def __init__(self, questao_dao_dependency: Questao_dao):
        print("⬆️ questao_service.__init__()")
        self.__questao_dao = questao_dao_dependency

    _campos_questao = [
        "assunto",
        "disciplina",
        "tipo_questao",
        "dificuldade",
        "enunciado"
    ]
    
    def criar(self, json_questao: dict):
        print("🟣 questao_service.criar()")

        obj_questao = Questao()
        self._setar_modelo_questao(obj_questao, json_questao)

        if self.__questao_dao.campo_existe("enunciado",obj_questao.enunciado):
            raise resposta_erro_http(
                400,
                "Enunciado repetido",
                {"mensagem":f'A questão de enunciado "{obj_questao.enunciado}" já está cadastrada'}
            )
        return self.__questao_dao.criar(obj_questao)
    

    
    def consulta(self, filtro) -> list[dict]:
        print("🟣 questao_service.consulta()")
        return self.__questao_dao.consulta(filtro)
    
    
    def atualizar(self, json_questao: dict, _id: str) -> bool:
        print("🟣 questao_service.atualizar()")

        obj_questao = Questao()
        self._setar_modelo_questao(obj_questao, json_questao)
        obj_questao.id_hash = _id
        return self.__questao_dao.atualizar(obj_questao)

    
    def excluir(self, _id: str) -> bool:
        print("🟣 questao_service.excluir()")
        obj_questao = Questao()
        obj_questao.id_hash = _id
        return self.__questao_dao.excluir(obj_questao.id_hash)
    
    def _setar_modelo_questao(self,obj_questao,json_questao):
        for campo in self._campos_questao:
            setattr(obj_questao, campo, json_questao.get(campo))
        
        dados_professor = json_questao.get("professor")
        professor = Usuario()
        professor.nome = dados_professor.get("nome")
        obj_questao.professor = professor

        if obj_questao.tipo_questao == "Objetiva":
            obj_questao.alternativas = json_questao.get("alternativas")
            obj_questao.alternativa_correta = json_questao.get("alternativa_correta")
        else:
            obj_questao.numero_linhas = json_questao.get("numero_linhas")

        if "autor" not in json_questao:
            obj_questao.autor = obj_questao.professor.nome
        else:
            obj_questao.autor = json_questao.get("autor")
