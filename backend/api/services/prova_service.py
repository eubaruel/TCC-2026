from api.modelos.prova import Prova
from api.modelos.disciplina import Disciplina
from api.modelos.usuario import Usuario
from api.DAOs.prova_dao import Prova_dao
from api.DAOs.questao_dao import Questao_dao

from api.utils.resposta_erro_http import resposta_erro_http


class Prova_service:
    def __init__(
        self,
        prova_dao_dependency: Prova_dao,
        questao_dao_dependency: Questao_dao
    ):
        print("⬆️ prova_service.__init__()")
        self.__prova_dao = prova_dao_dependency
        self.__questao_dao = questao_dao_dependency

    _CAMPOS_PROVA = [
        "id_turma",
        "status",
        "tipo",
        "serie",
        "bimestre",
        "data_de_aplicacao"
    ]

    def criar(self, json_prova: dict):
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
                {"mensagem": "A prova com Id fornecido não existe no banco de dados"}
            )

        return self.__prova_dao.atualizar(obj_prova)

    def excluir(self, id_hash: str) -> bool:
        print("🟣 prova_service.excluir()")
        obj_prova = Prova()
        obj_prova.id_hash = id_hash
        return self.__prova_dao.excluir(obj_prova.id_hash)

    def _setar_modelo_prova(self, obj_prova, json_prova):
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

        obj_prova.questoes = self._validar_ids_questoes(
            json_prova.get("questoes"),
            obj_prova
        )

    def _validar_ids_questoes(self, ids_questoes, obj_prova):
        if not isinstance(ids_questoes, list):
            raise resposta_erro_http(
                400,
                "Questões inválidas",
                {"mensagem": "O campo 'questoes' deve ser uma lista de ids"}
            )

        if len(ids_questoes) < 3:
            raise resposta_erro_http(
                400,
                "Número de questões insuficiente",
                {"mensagem": "A prova deve possuir ao menos cinco questões"}
            )

        ids_normalizados = []
        for indice, id_questao in enumerate(ids_questoes, start=1):
            if not isinstance(id_questao, str):
                raise resposta_erro_http(
                    400,
                    "Id de questão inválido",
                    {"mensagem": f"O id da questão {indice} deve ser uma string"}
                )

            id_questao = id_questao.strip()
            if not id_questao:
                raise resposta_erro_http(
                    400,
                    "Id de questão inválido",
                    {"mensagem": f"O id da questão {indice} não pode ser vazio"}
                )
            ids_normalizados.append(id_questao)

        if len(ids_normalizados) != len(set(ids_normalizados)):
            raise resposta_erro_http(
                400,
                "Questões repetidas",
                {"mensagem": "A prova não pode conter ids de questões repetidos"}
            )

        questoes = self.__questao_dao.buscar_por_ids(ids_normalizados)
        questoes_por_id = {
            questao["_id"]: questao
            for questao in questoes
        }

        ids_ausentes = [
            id_questao
            for id_questao in ids_normalizados
            if id_questao not in questoes_por_id
        ]
        if ids_ausentes:
            raise resposta_erro_http(
                400,
                "Questão não encontrada",
                {"mensagem": "Uma ou mais questões não existem ou estão inativas"}
            )

        referencias_disciplina = {
            obj_prova.disciplina.codigo_disciplina.strip().casefold(),
            obj_prova.disciplina.nome_disciplina.strip().casefold()
        }

        for indice, id_questao in enumerate(ids_normalizados, start=1):
            questao = questoes_por_id[id_questao]
            tipo_questao = str(questao.get("tipo_questao", "")).strip().title()
            if tipo_questao != obj_prova.tipo:
                raise resposta_erro_http(
                    400,
                    "Tipo de questão incompatível",
                    {"mensagem": f"A questão {indice} não é do tipo {obj_prova.tipo}"}
                )

            disciplinas_questao = {
                str(valor).strip().casefold()
                for valor in questao.get("disciplina", [])
            }
            if not referencias_disciplina.intersection(disciplinas_questao):
                raise resposta_erro_http(
                    400,
                    "Disciplina incompatível",
                    {"mensagem": f"A questão {indice} não pertence à disciplina da prova"}
                )

        return ids_normalizados
