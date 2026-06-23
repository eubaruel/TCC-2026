from api.modelos.aluno import Aluno
from api.DAOs.aluno_dao import Aluno_dao

from api.utils.resposta_erro_http import resposta_erro_http
import pandas as pd

class Aluno_service:
    def __init__(self, aluno_dao_dependency: Aluno_dao):
        print("⬆️ aluno_service.__init__()")
        self.__aluno_dao = aluno_dao_dependency

    _CAMPOS_ALUNO = [
        "nome_aluno",
        "turma",
        "serie",
        "situacao",
        "email_aluno"
    ]    
    
    def criar(self, json_aluno: dict) -> bool:
        print("🟣 aluno_service.criar()")

        obj_aluno = Aluno()
        self._setar_modelo_aluno(obj_aluno, json_aluno)

        matricula_existe = self.__aluno_dao.campo_existe("matricula_aluno",obj_aluno.matricula_aluno)
        if matricula_existe:
            raise resposta_erro_http(
                400,
                "Matrícula repetida",
                {"mensagem":f"O aluno com a matrícula {obj_aluno.matricula_aluno} já está cadastrado"}
            )
        return self.__aluno_dao.criar(obj_aluno)
    
    def importar_excel(self, df) ->int:
        print("🟣 aluno_service.importar_excel()")

        docs = []
        
        inseridos = 0

        for _, linha in df.iterrows():
            if linha.isnull().any():
                print("❌ Linha com valor nulo:", linha)
                continue
            try:
                doc = self._ler_linha(linha)

                if doc:
                    docs.append(doc)
                    inseridos += 1
                else:
                    continue

            except Exception as e:
                print(f"Erro na linha: {linha} → {e}")
                continue

        if docs:
            self.__aluno_dao.importar_excel(docs)

        return inseridos
    
    
    def consulta(self, filtro) -> list[dict]:
        print("🟣 aluno_service.consulta()")
        return self.__aluno_dao.consulta(filtro)
    
    
    def atualizar(self, json_aluno: dict, matricula_aluno: int) -> bool:
        print("🟣 aluno_service.atualizar()")

        obj_aluno = Aluno()
        obj_aluno.matricula_aluno = matricula_aluno
        self._setar_modelo_aluno(obj_aluno, json_aluno)

        matricula_existe = self.__aluno_dao.campo_existe("matricula_aluno",obj_aluno.matricula_aluno)
        if not matricula_existe:
            raise resposta_erro_http(
                400,
                "Matrícula repetida",
                {"mensagem":f"O aluno com a matrícula {obj_aluno.matricula_aluno} não está cadastrado"}
            )
        
        return self.__aluno_dao.atualizar(obj_aluno)
    
    
    def excluir(self, matricula_aluno: int) -> bool:
        print("🟣 aluno_service.excluir()")
        obj_aluno = Aluno()
        obj_aluno.matricula_aluno = matricula_aluno
        return self.__aluno_dao.excluir(obj_aluno.matricula_aluno)


    def _setar_modelo_aluno(self, obj_aluno ,json_aluno):
        for campo in self._CAMPOS_ALUNO:
            setattr(obj_aluno, campo, json_aluno.get(campo))
        obj_aluno.ativo = True

    def _ler_linha(self, linha):

        obj_aluno = Aluno()

        obj_aluno.matricula_aluno = int(linha["matrícula"])
        obj_aluno.nome_aluno = linha["nome"]
        obj_aluno.turma = linha["turma"]
        obj_aluno.serie = int(linha["série"])
        obj_aluno.situacao = linha["situação"]
        obj_aluno.email_aluno = linha["email"]
        obj_aluno.ativo = True

        if self.__aluno_dao.campo_existe("matricula_aluno",obj_aluno.matricula_aluno):
            return None

        doc = self.__aluno_dao.set_doc(obj_aluno)
        doc['matricula_aluno'] = obj_aluno.matricula_aluno

        return doc




