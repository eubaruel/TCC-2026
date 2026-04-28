from api.modelos.disciplina import Disciplina
from api.DAOs.disciplina_dao import Disciplina_dao

from api.modelos.usuario import Usuario

from api.utils.resposta_erro import resposta_erro

class Disciplina_service:
    def __init__(self, disciplina_dao_dependency: Disciplina_dao):
        print("⬆️ disciplina_service.__init__()")
        self.__disciplina_dao = disciplina_dao_dependency

    
    def criar(self, json_disciplina: dict) -> bool:
        print("🟣 disciplina_service.criar()")

        obj_disciplina = Disciplina()
        self.setar_modelo_disciplina(obj_disciplina, json_disciplina)

        codigo_existe = self.__disciplina_dao.campo_existe("codigo_disciplina",obj_disciplina.codigo_disciplina)
        if codigo_existe:
            raise resposta_erro(
                400,
                "Código repetido",
                {"mensagem":f"A disciplina com o código {obj_disciplina.codigo_disciplina} já está cadastrado"}
            )
        return self.__disciplina_dao.criar(obj_disciplina)
    
    
    def consulta(self, filtro) -> list[dict]:
        print("🟣 disciplina_service.consulta()")
        return self.__disciplina_dao.consulta(filtro)
    

    def atualizar(self, json_disciplina: dict, filtro) -> bool:
        print("🟣 disciplina_service.atualizar()")

        obj_disciplina = Disciplina()
        self.setar_modelo_disciplina(obj_disciplina, json_disciplina)
        return self.__disciplina_dao.atualizar(obj_disciplina, filtro)
    

    def excluir(self, codigo_disciplina: int) -> bool:
        print("🟣 disciplina_service.excluir()")
        obj_disciplina = Disciplina()
        obj_disciplina.codigo_disciplina = codigo_disciplina
        return self.__disciplina_dao.excluir(obj_disciplina.codigo_disciplina)
    
        
    def setar_modelo_disciplina(self, obj_disciplina, json_disciplina):
        obj_disciplina.codigo_disciplina = json_disciplina.get("codigo_disciplina")
        obj_disciplina.nome_disciplina = json_disciplina.get("nome_disciplina")
        obj_disciplina.turma = json_disciplina.get("turma")
        obj_disciplina.alunos = json_disciplina.get("alunos")

        dados_professor = json_disciplina.get("professor")
        professsor = Usuario()
        professsor.registro = dados_professor.get("registro")
        professsor.nome = dados_professor.get("nome")

        obj_disciplina.professor = professsor