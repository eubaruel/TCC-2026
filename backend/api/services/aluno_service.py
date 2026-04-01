from api.modelos.aluno import Aluno
from api.DAOs.aluno_dao import Aluno_dao

from api.utils.resposta_erro import resposta_erro

class Aluno_service:
    def __init__(self, aluno_dao_dependency: Aluno_dao):
        print("⬆️ aluno_service.__init__()")
        self.__aluno_dao = aluno_dao_dependency
    
    
    def criar(self, json_aluno: dict) -> bool:
        print("🟣 aluno_service.criar()")

        obj_aluno = Aluno()
        self.setar_modelo_aluno(obj_aluno, json_aluno)

        matricula_existe = self.__aluno_dao.campo_existe("matricula_aluno",obj_aluno.matricula_aluno)
        if matricula_existe:
            raise resposta_erro(
                400,
                "Matrícula repitida",
                {"mensagem":f"O aluno com a matrícula {obj_aluno.matricula_aluno} já está cadastrado"}
            )
        return self.__aluno_dao.criar(obj_aluno)
    
    
    def consulta(self, filtro) -> list[dict]:
        print("🟣 aluno_service.consulta()")
        return self.__aluno_dao.consulta(filtro)
    
    
    def atualizar(self, json_aluno: dict) -> bool:
        print("🟣 aluno_service.atualizar()")

        obj_aluno = Aluno()
        self.setar_modelo_aluno(obj_aluno, json_aluno)
        return self.__aluno_dao.atualizar(obj_aluno)
    
    
    def excluir(self, matricula_aluno: int) -> bool:
        print("🟣 aluno_service.excluir()")
        obj_aluno = Aluno()
        obj_aluno.matricula_aluno = matricula_aluno
        return self.__aluno_dao.excluir(obj_aluno.matricula_aluno)


    def setar_modelo_aluno(self, obj_aluno ,json_aluno):
        obj_aluno.matricula_aluno = json_aluno.get("matricula_aluno")
        obj_aluno.nome_aluno = json_aluno.get("nome_aluno")
        obj_aluno.turma = json_aluno.get("turma")
        obj_aluno.serie = json_aluno.get("serie")
        obj_aluno.situacao = json_aluno.get("situacao")
        obj_aluno.email_aluno = json_aluno.get("email_aluno")





