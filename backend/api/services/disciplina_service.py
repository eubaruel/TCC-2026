from api.modelos.disciplina import Disciplina
from api.DAOs.disciplina_dao import Disciplina_dao

from api.modelos.usuario import Usuario

from api.utils.resposta_erro_http import resposta_erro_http

class Disciplina_service:
    def __init__(self, disciplina_dao_dependency: Disciplina_dao):
        print("⬆️ disciplina_service.__init__()")
        self.__disciplina_dao = disciplina_dao_dependency

    _CAMPOS_DISCIPLINA = ["nome_disciplina",
                        "turma",
                        "alunos",
                        ]
    
    _CAMPOS_PROFESSOR = ["nome","registro"]

    
    def criar(self, json_disciplina: dict) -> bool:
        print("🟣 disciplina_service.criar()")

        obj_disciplina = Disciplina()
        self.setar_modelo_disciplina(obj_disciplina, json_disciplina)
        obj_disciplina.codigo_disciplina = json_disciplina.get("codigo_disciplina")

        codigo_existe = self.__disciplina_dao.campo_existe("codigo_disciplina",obj_disciplina.codigo_disciplina)
        if codigo_existe:
            raise resposta_erro_http(
                400,
                "Código repetido",
                {"mensagem":f"A disciplina com o código {obj_disciplina.codigo_disciplina} já está cadastrado"}
            )
        return self.__disciplina_dao.criar(obj_disciplina)
    
    
    def consulta(self, filtro) -> list[dict]:
        print("🟣 disciplina_service.consulta()")
        disciplinas = self.__disciplina_dao.consulta(filtro)
        for disciplina in disciplinas:
            alunos = disciplina.pop("alunos", [])
            disciplina.pop("ativo", None)
            disciplina["quantidade_alunos"] = len(alunos)
        return disciplinas
    

    def atualizar(self, json_disciplina: dict, codigo_disciplina: str) -> bool:
        print("🟣 disciplina_service.atualizar()")

        obj_disciplina = Disciplina()
        self.setar_modelo_disciplina(obj_disciplina, json_disciplina)
        obj_disciplina.codigo_disciplina = codigo_disciplina
        return self.__disciplina_dao.atualizar(obj_disciplina)
    

    def excluir(self, codigo_disciplina: str) -> bool:
        print("🟣 disciplina_service.excluir()")
        obj_disciplina = Disciplina()
        obj_disciplina.codigo_disciplina = codigo_disciplina
        return self.__disciplina_dao.excluir(obj_disciplina.codigo_disciplina)
    
        
    def setar_modelo_disciplina(self, obj_disciplina, json_disciplina):
        for campo in self._CAMPOS_DISCIPLINA:
            setattr(obj_disciplina, campo, json_disciplina.get(campo))

        dados_professor = json_disciplina.get("professor")
        professor = Usuario()
        for campo in self._CAMPOS_PROFESSOR:
            setattr(professor,campo,dados_professor.get(campo))

        obj_disciplina.professor = professor
