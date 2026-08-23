import random
from copy import deepcopy

from api.DAOs.aluno_dao import Aluno_dao
from api.DAOs.prova_x_aluno_dao import Prova_x_aluno_dao
from api.DAOs.questao_dao import Questao_dao
from api.modelos.prova_x_aluno import Prova_x_aluno
from api.utils.resposta_erro_http import resposta_erro_http


class Prova_x_aluno_service:
    def __init__(
        self,
        aluno_dao_dependency: Aluno_dao,
        prova_x_aluno_dao_dependency: Prova_x_aluno_dao,
        questao_dao_dependency: Questao_dao,
        gerador_aleatorio_dependency=None
    ):
        print("⬆️ prova_x_aluno_service.__init__()")
        self.__aluno_dao = aluno_dao_dependency
        self.__prova_x_aluno_dao = prova_x_aluno_dao_dependency
        self.__questao_dao = questao_dao_dependency
        self.__gerador_aleatorio = gerador_aleatorio_dependency or random.SystemRandom()

    def gerar(self, id_prova: str, id_turma, ids_questoes: list[str]) -> int:
        print("🟣 prova_x_aluno_service.gerar()")

        turmas = self._normalizar_turmas(id_turma)
        matriculas = self.__aluno_dao.buscar_matriculas_por_turmas(turmas)

        provas_x_alunos = []
        for matricula in dict.fromkeys(matriculas):
            obj_prova_x_aluno = Prova_x_aluno()
            obj_prova_x_aluno.matricula_aluno = matricula
            obj_prova_x_aluno.id_prova = id_prova
            obj_prova_x_aluno.questoes = self._gerar_questoes(ids_questoes)
            provas_x_alunos.append(obj_prova_x_aluno)

        return self.__prova_x_aluno_dao.sincronizar(id_prova, provas_x_alunos)

    def montar_para_impressao(self, id_prova: str) -> list[dict]:
        print("🟣 prova_x_aluno_service.montar_para_impressao()")

        registros = self.__prova_x_aluno_dao.buscar_por_id_prova(id_prova)
        if not registros:
            return []

        ids_questoes = list(dict.fromkeys(
            questao["id_questao"]
            for registro in registros
            for questao in registro.get("questoes", [])
        ))
        questoes = self.__questao_dao.buscar_por_ids(ids_questoes)
        questoes_por_id = {
            questao["_id"]: questao
            for questao in questoes
        }

        ids_ausentes = [
            id_questao
            for id_questao in ids_questoes
            if id_questao not in questoes_por_id
        ]
        if ids_ausentes:
            raise resposta_erro_http(
                404,
                "Questão não encontrada",
                {
                    "mensagem":
                    "Uma ou mais questões da prova não existem ou estão inativas"
                }
            )

        provas_alunos = []
        for registro in registros:
            questoes_aluno = []
            for configuracao in registro.get("questoes", []):
                questao = deepcopy(
                    questoes_por_id[configuracao["id_questao"]]
                )
                self._embaralhar_alternativas(
                    questao,
                    configuracao["posicao_alternativa_correta"]
                )
                questoes_aluno.append(questao)

            provas_alunos.append({
                "matricula_aluno": registro["matricula_aluno"],
                "questoes": questoes_aluno
            })

        return provas_alunos

    def _gerar_questoes(self, ids_questoes: list[str]) -> list[dict]:
        ordem_original = list(ids_questoes)
        ordem_embaralhada = self.__gerador_aleatorio.sample(
            ordem_original,
            len(ordem_original)
        )

        # Para duas ou mais questões, garante que a versão do aluno não preserve
        # acidentalmente a mesma ordem da prova-base.
        if len(ordem_embaralhada) > 1 and ordem_embaralhada == ordem_original:
            ordem_embaralhada = ordem_embaralhada[1:] + ordem_embaralhada[:1]

        return [
            {
                "id_questao": id_questao,
                "posicao_alternativa_correta": self.__gerador_aleatorio.randint(1, 5)
            }
            for id_questao in ordem_embaralhada
        ]

    def _embaralhar_alternativas(
        self,
        questao: dict,
        posicao_alternativa_correta: int
    ) -> None:
        alternativas = questao.get("alternativas")
        id_alternativa_correta = questao.get("alternativa_correta")

        if not isinstance(alternativas, list) or not alternativas:
            raise resposta_erro_http(
                400,
                "Questão inválida",
                {"mensagem": "Uma questão objetiva não possui alternativas válidas"}
            )

        alternativa_correta = next(
            (
                alternativa
                for alternativa in alternativas
                if alternativa.get("id") == id_alternativa_correta
            ),
            None
        )
        if alternativa_correta is None:
            raise resposta_erro_http(
                400,
                "Questão inválida",
                {
                    "mensagem":
                    "A alternativa correta não foi encontrada entre as alternativas"
                }
            )

        if (
            not isinstance(posicao_alternativa_correta, int)
            or isinstance(posicao_alternativa_correta, bool)
        ):
            raise resposta_erro_http(
                400,
                "Posição da alternativa correta inválida",
                {"mensagem": "A posição da alternativa correta deve ser um inteiro"}
            )

        indice_alternativa_correta = posicao_alternativa_correta - 1
        if indice_alternativa_correta not in range(len(alternativas)):
            raise resposta_erro_http(
                400,
                "Posição da alternativa correta inválida",
                {
                    "mensagem":
                    "A posição da alternativa correta não cabe no vetor de alternativas"
                }
            )

        alternativas_incorretas = [
            alternativa
            for alternativa in alternativas
            if alternativa.get("id") != id_alternativa_correta
        ]
        self.__gerador_aleatorio.shuffle(alternativas_incorretas)
        alternativas_incorretas.insert(
            indice_alternativa_correta,
            alternativa_correta
        )
        questao["alternativas"] = alternativas_incorretas

    @staticmethod
    def _normalizar_turmas(id_turma) -> list[str]:
        turmas = id_turma if isinstance(id_turma, list) else [id_turma]
        return list(dict.fromkeys(turmas))
