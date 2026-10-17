from api.modelos.prova import Prova
from api.modelos.disciplina import Disciplina
from api.modelos.usuario import Usuario
from api.DAOs.prova_dao import Prova_dao
from api.DAOs.questao_dao import Questao_dao
from api.services.prova_x_aluno_service import Prova_x_aluno_service

from api.utils.resposta_erro_http import resposta_erro_http
from html import unescape
from contextlib import contextmanager
from uuid import uuid4
import re


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
        "periodo_letivo",
        "data_de_aplicacao"
    ]

    def criar_prova(self, json_prova: dict) -> dict:
        """Cria uma prova-base que ainda aguarda a seleção das questões."""
        print("🟣 prova_service.criar_prova()")

        obj_prova = Prova()
        self._setar_dados_base(obj_prova, json_prova, exigir_registro=True)
        obj_prova.quantidade_questoes = json_prova.get("quantidade_questoes")
        obj_prova.status = "Aguardando questões"
        obj_prova.questoes = []

        id_criado = self.__prova_dao.criar(obj_prova)
        return self._formatar_prova(obj_prova, id_criado)

    def adicionar_questoes(self, id_hash: str, ids_questoes: list) -> dict:
        print("🟣 prova_service.adicionar_questoes()")
        with self._operacao_exclusiva(id_hash) as token:
            prova = self._buscar_prova(id_hash)
            self._exigir_edicao(prova)
            geracao_pendente = prova.pop("geracao_pendente", False)
            ids_normalizados = self._validar_ids_questoes(
                ids_questoes, prova.get("tipo"), prova.get("disciplina")
            )
            self._validar_quantidade_questoes(prova, ids_normalizados)
            quantidade = self.__prova_x_aluno_service.quantidade_versoes(id_hash, ids_normalizados, prova["id_turma"])
            mesmas_questoes = prova.get("questoes") == ids_normalizados
            if mesmas_questoes and quantidade and not geracao_pendente:
                if prova["status"] != "Em elaboração":
                    if not self.__prova_dao.atualizar_questoes(id_hash, ids_normalizados, token=token):
                        raise resposta_erro_http(409, "A prova não está mais disponível para edição")
                    prova["status"] = "Em elaboração"
                return {"prova": prova, "provas_alunos_geradas": quantidade, "versoes_regeneradas": False}

            if not self.__prova_dao.atualizar_questoes(id_hash, ids_normalizados, token=token, geracao_pendente=True):
                raise resposta_erro_http(409, "A prova não está mais disponível para edição")
            provas_alunos_geradas = self.__prova_x_aluno_service.gerar(
                id_hash, prova.get("id_turma"), ids_normalizados
            )
            if not self.__prova_dao.concluir_geracao(id_hash, token):
                raise resposta_erro_http(409, "Não foi possível confirmar a geração das versões individuais")
            return {
                "prova": {**prova, "questoes": ids_normalizados, "status": "Em elaboração"},
                "provas_alunos_geradas": provas_alunos_geradas,
                "versoes_regeneradas": True
            }

    def enviar(self, id_hash: str) -> dict:
        with self._operacao_exclusiva(id_hash) as token:
            prova = self._buscar_prova(id_hash)
            if prova["status"] != Prova.STATUS_ENVIADA:
                self._exigir_edicao(prova)
            if prova.pop("geracao_pendente", False):
                raise resposta_erro_http(409, "Geração de versões pendente",
                                        {"mensagem": "Salve a seleção novamente para completar a geração antes de enviar"})
            ids = self._validar_ids_questoes(prova.get("questoes"), prova["tipo"], prova["disciplina"])
            self._validar_quantidade_questoes(prova, ids, completa=True)
            quantidade = self.__prova_x_aluno_service.quantidade_versoes(
                id_hash, ids, prova["id_turma"] if prova["status"] != Prova.STATUS_ENVIADA else None
            )
            if not quantidade:
                raise resposta_erro_http(409, "Nenhuma versão individual disponível",
                                        {"mensagem": "Confira os alunos ativos das turmas e salve a seleção novamente antes de enviar"})
            if prova["status"] != Prova.STATUS_ENVIADA:
                if not self.__prova_dao.enviar(id_hash, ids, token=token):
                    raise resposta_erro_http(409, "A prova mudou durante o envio. Atualize a tela e tente novamente")
                prova["status"] = Prova.STATUS_ENVIADA
            return {"prova": prova, "provas_alunos_geradas": quantidade}

    def confirmar_impressao(self, id_hash: str) -> dict:
        with self._operacao_exclusiva(id_hash) as token:
            prova = self._buscar_prova(id_hash)
            if prova["status"] not in (Prova.STATUS_ENVIADA, Prova.STATUS_IMPRESSA):
                raise resposta_erro_http(409, "Apenas provas enviadas podem ter a impressão confirmada")
            if prova.get("geracao_pendente"):
                raise resposta_erro_http(409, "Geração de versões pendente")
            ids = self._validar_ids_questoes(prova.get("questoes"), prova["tipo"], prova["disciplina"])
            self._validar_quantidade_questoes(prova, ids, completa=True)
            if not self.__prova_x_aluno_service.quantidade_versoes(id_hash, ids):
                raise resposta_erro_http(409, "Nenhuma versão individual disponível")
            if prova["status"] != Prova.STATUS_IMPRESSA:
                if not self.__prova_dao.confirmar_impressao(id_hash, token):
                    raise resposta_erro_http(409, "A prova mudou durante a confirmação. Atualize a tela e tente novamente")
                prova["status"] = Prova.STATUS_IMPRESSA
            return {"prova": prova}

    @contextmanager
    def _operacao_exclusiva(self, id_hash):
        # Reserva no banco: protege também requisições atendidas por processos distintos.
        token = uuid4().hex
        if not self.__prova_dao.reservar_operacao(id_hash, token):
            self._buscar_prova(id_hash)
            raise resposta_erro_http(409, "Há outra operação em andamento nesta prova. Aguarde e tente novamente")
        try:
            yield token
        finally:
            self.__prova_dao.liberar_operacao(id_hash, token)

    def _buscar_prova(self, id_hash):
        prova = self.__prova_dao.buscar_por_id(id_hash)
        if not prova:
            raise resposta_erro_http(404, "Prova não encontrada")
        return prova

    @staticmethod
    def _exigir_edicao(prova):
        if prova.get("status") not in Prova.STATUS_EDITAVEIS:
            raise resposta_erro_http(409, "Prova concluída não pode ser editada")

    def consulta(self, filtro) -> list[dict]:
        print("🟣 prova_service.consulta()")
        return self.__prova_dao.consulta(filtro)

    def imprimir_provas(self, id_hash: str) -> list[dict]:
        print("🟣 prova_service.imprimir_provas()")
        prova = self._buscar_prova(id_hash)
        if prova.get("status") in Prova.STATUS_EDITAVEIS:
            raise resposta_erro_http(409, "Conclua e envie a prova antes de imprimir")
        self._validar_quantidade_questoes(prova, prova.get("questoes", []), completa=True)
        versoes = self.__prova_x_aluno_service.montar_para_impressao(id_hash)
        for versao in versoes:
            self._validar_quantidade_questoes(prova, versao["questoes"], completa=True)
        return versoes

    def atualizar(self, json_prova: dict, id_hash: str) -> bool:
        print("🟣 prova_service.atualizar()")
        with self._operacao_exclusiva(id_hash) as token:
            prova = self._buscar_prova(id_hash)
            self._exigir_edicao(prova)
            # PUT não deve contornar a seleção de questões ou a conclusão dedicada.
            if prova.get("quantidade_questoes") is not None:
                json_prova.setdefault("quantidade_questoes", prova["quantidade_questoes"])
                if json_prova["quantidade_questoes"] is None:
                    raise resposta_erro_http(400, "Quantidade de questões deve ser um inteiro de 2 a 10")
            if json_prova.get("status") != prova["status"] or json_prova.get("questoes") != prova["questoes"]:
                raise resposta_erro_http(400, "Use as rotas adicionar-questoes e enviar para alterar o fluxo da prova")
            if prova["questoes"] and any(json_prova.get(campo) != prova.get(campo)
                                         for campo in self._CAMPOS_PROVA_BASE + ["professor", "disciplina", "quantidade_questoes"]):
                raise resposta_erro_http(409, "Os metadados não podem mudar após vincular questões à prova")

            obj_prova = Prova()
            self._setar_modelo_prova(obj_prova, json_prova)
            obj_prova.id_hash = id_hash

            if not self.__prova_dao.campo_existe("_id", obj_prova.id_hash):
                raise resposta_erro_http(
                    400,
                    "Prova não existe",
                    {"mensagem": "A prova com Id fornecido não existe no banco de dados"}
                )
            return self.__prova_dao.atualizar(obj_prova, token=token)

    def excluir(self, id_hash: str) -> bool:
        print("🟣 prova_service.excluir()")
        with self._operacao_exclusiva(id_hash) as token:
            self._exigir_edicao(self._buscar_prova(id_hash))
            obj_prova = Prova()
            obj_prova.id_hash = id_hash
            return self.__prova_dao.excluir(obj_prova.id_hash, token=token)

    def _setar_modelo_prova(self, obj_prova, json_prova):
        self._setar_dados_base(obj_prova, json_prova, exigir_registro=True)
        if json_prova.get("quantidade_questoes") is not None:
            obj_prova.quantidade_questoes = json_prova["quantidade_questoes"]
        obj_prova.status = json_prova.get("status")

        obj_prova.questoes = json_prova.get("questoes")

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
            "periodo_letivo": obj_prova.periodo_letivo,
            "data_de_aplicacao": obj_prova.data_de_aplicacao,
            "questoes": obj_prova.questoes,
            "quantidade_questoes": obj_prova.quantidade_questoes
        }

    @staticmethod
    def _validar_quantidade_questoes(prova, ids_questoes, completa=False):
        quantidade = prova.get("quantidade_questoes")
        # Bases antigas não possuem quantidade definida pelo pedagógico.
        if quantidade is not None and (len(ids_questoes) > quantidade or completa and len(ids_questoes) != quantidade):
            raise resposta_erro_http(
                400, "Quantidade de questões incompatível",
                {"mensagem": f"A prova exige {quantidade} questões para concluir; não selecione mais que esse total"}
            )

    def _validar_ids_questoes(
        self,
        ids_questoes,
        tipo_prova,
        disciplina_prova
    ):
        if str(tipo_prova).strip().title() != "Objetiva":
            raise resposta_erro_http(
                400,
                "Tipo de prova inválido",
                {"mensagem": "Apenas provas objetivas são permitidas"}
            )

        if not isinstance(ids_questoes, list):
            raise resposta_erro_http(
                400,
                "Questões inválidas",
                {"mensagem": "O campo 'questoes' deve ser uma lista de ids"}
            )

        if len(ids_questoes) < 2:
            raise resposta_erro_http(
                400,
                "Número de questões insuficiente",
                {"mensagem": "Informe ao menos duas questões"}
            )

        if len(ids_questoes) > Prova.MAX_QUESTOES:
            raise resposta_erro_http(
                400,
                "Limite de questões excedido",
                {"mensagem": f"A prova deve ter de 2 a {Prova.MAX_QUESTOES} questões"}
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

            alternativas = questao.get("alternativas", [])
            if (not self._conteudo_preenchido(questao.get("enunciado"))
                    or not isinstance(alternativas, list) or len(alternativas) != 5
                    or any(not isinstance(item, dict) or not item.get("id")
                           or not self._conteudo_preenchido(item.get("texto")) for item in alternativas)
                    or len({item["id"] for item in alternativas}) != 5
                    or len({item["texto"].strip() for item in alternativas}) != 5
                    or questao.get("alternativa_correta") not in {item["id"] for item in alternativas}):
                raise resposta_erro_http(400, "Questão incompleta",
                                        {"mensagem": f"Questão {indice}: confira enunciado, cinco alternativas distintas e alternativa correta no banco"})

        return ids_normalizados

    @staticmethod
    def _conteudo_preenchido(valor):
        if not isinstance(valor, str):
            return False
        return bool(unescape(re.sub(r"<[^>]*>", "", valor)).strip()
                    or re.search(r"<img\b[^>]*\bsrc\s*=", valor, re.IGNORECASE))
