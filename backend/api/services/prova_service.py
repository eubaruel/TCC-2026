from api.modelos.prova import Prova
from api.modelos.disciplina import Disciplina
from api.modelos.usuario import Usuario
from api.DAOs.prova_dao import Prova_dao
from api.DAOs.questao_dao import Questao_dao
from api.services.prova_x_aluno_service import Prova_x_aluno_service

from api.utils.resposta_erro_http import resposta_erro_http


class Prova_service:
    def __init__(
        self,
        prova_dao_dependency: Prova_dao,
        questao_dao_dependency: Questao_dao,
        prova_x_aluno_service_dependency: Prova_x_aluno_service
    ):
        print("⬆️ prova_service.__init__()")
        self.__prova_dao = prova_dao_dependency
        self.__questao_dao = questao_dao_dependency
        self.__prova_x_aluno_service = prova_x_aluno_service_dependency

    _CAMPOS_PROVA_BASE = [
        "id_turma",
        "tipo",
        "serie",
        "bimestre",
        "data_de_aplicacao"
    ]

    def criar_prova(self, json_prova: dict) -> dict:
        """Cria uma prova-base que ainda aguarda a seleção das questões."""
        print("🟣 prova_service.criar_prova()")

        obj_prova = Prova()
        self._setar_dados_base(obj_prova, json_prova, exigir_registro=True)
        obj_prova.status = "Aguardando questões"
        obj_prova.questoes = []

        id_criado = self.__prova_dao.criar(obj_prova)
        return self._formatar_prova(obj_prova, id_criado)

    def adicionar_questoes(self, id_hash: str, ids_questoes: list) -> dict:
        print("🟣 prova_service.adicionar_questoes()")

        prova = self.__prova_dao.buscar_por_id(id_hash)
        if not prova:
            raise resposta_erro_http(
                404,
                "Prova não encontrada",
                {"mensagem": "A prova informada não existe ou está inativa"}
            )

        ids_normalizados = self._validar_ids_questoes(
            ids_questoes,
            prova.get("tipo"),
            prova.get("disciplina")
        )

        if not self.__prova_dao.atualizar_questoes(id_hash, ids_normalizados):
            raise resposta_erro_http(
                404,
                "Prova não encontrada",
                {"mensagem": "A prova informada não existe ou está inativa"}
            )

        provas_alunos_geradas = 0
        if str(prova.get("tipo", "")).strip().casefold() == "objetiva":
            provas_alunos_geradas = self.__prova_x_aluno_service.gerar(
                id_hash,
                prova.get("id_turma"),
                ids_normalizados
            )

        return {
            "prova": {
                "_id": id_hash,
                "questoes": ids_normalizados
            },
            "provas_alunos_geradas": provas_alunos_geradas
        }

    def consulta(self, filtro) -> list[dict]:
        print("🟣 prova_service.consulta()")
        return self.__prova_dao.consulta(filtro)

    def imprimir_provas(self, id_hash: str) -> list[dict]:
        print("🟣 prova_service.imprimir_provas()")
        return self.__prova_x_aluno_service.montar_para_impressao(id_hash)

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
        self._setar_dados_base(obj_prova, json_prova)
        obj_prova.status = json_prova.get("status")

        obj_prova.questoes = self._validar_ids_questoes(
            json_prova.get("questoes"),
            obj_prova.tipo,
            {
                "codigo_disciplina": obj_prova.disciplina.codigo_disciplina,
                "nome_disciplina": obj_prova.disciplina.nome_disciplina
            }
        )

    def _setar_dados_base(self, obj_prova, json_prova, exigir_registro=False):
        for campo in self._CAMPOS_PROVA_BASE:
            setattr(obj_prova, campo, json_prova.get(campo))

        dados_professor = json_prova.get("professor")
        professor = Usuario()
        if exigir_registro or "registro" in dados_professor:
            professor.registro = dados_professor.get("registro")
        professor.nome = dados_professor.get("nome")
        obj_prova.professor = professor

        dados_disciplina = json_prova.get("disciplina")
        disciplina = Disciplina()
        disciplina.codigo_disciplina = dados_disciplina.get("codigo_disciplina")
        disciplina.nome_disciplina = dados_disciplina.get("nome_disciplina")
        obj_prova.disciplina = disciplina

    def _formatar_prova(self, obj_prova, id_criado):
        professor = {
            "nome": obj_prova.professor.nome
        }
        if obj_prova.professor.registro is not None:
            professor["registro"] = obj_prova.professor.registro

        return {
            "_id": id_criado,
            "id_turma": obj_prova.id_turma,
            "professor": professor,
            "disciplina": {
                "codigo_disciplina": obj_prova.disciplina.codigo_disciplina,
                "nome_disciplina": obj_prova.disciplina.nome_disciplina
            },
            "status": obj_prova.status,
            "tipo": obj_prova.tipo,
            "serie": obj_prova.serie,
            "bimestre": obj_prova.bimestre,
            "data_de_aplicacao": obj_prova.data_de_aplicacao,
            "questoes": obj_prova.questoes
        }

    def _validar_ids_questoes(
        self,
        ids_questoes,
        tipo_prova,
        disciplina_prova
    ):
        if not isinstance(ids_questoes, list):
            raise resposta_erro_http(
                400,
                "Questões inválidas",
                {"mensagem": "O campo 'questoes' deve ser uma lista de ids"}
            )

        if not ids_questoes:
            raise resposta_erro_http(
                400,
                "Número de questões insuficiente",
                {"mensagem": "Informe ao menos uma questão"}
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

        disciplina_prova = disciplina_prova or {}
        referencias_disciplina = {
            str(disciplina_prova.get("codigo_disciplina", "")).strip().casefold(),
            str(disciplina_prova.get("nome_disciplina", "")).strip().casefold()
        }
        referencias_disciplina.discard("")
        tipo_prova = str(tipo_prova).strip().title()

        for indice, id_questao in enumerate(ids_normalizados, start=1):
            questao = questoes_por_id[id_questao]
            tipo_questao = str(questao.get("tipo_questao", "")).strip().title()
            if tipo_questao != tipo_prova:
                raise resposta_erro_http(
                    400,
                    "Tipo de questão incompatível",
                    {"mensagem": f"A questão {indice} não é do tipo {tipo_prova}"}
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
