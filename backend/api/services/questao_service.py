from uuid import uuid4

from api.modelos.alternativa import Alternativa
from api.modelos.questao import Questao
from api.modelos.usuario import Usuario
from api.DAOs.questao_dao import Questao_dao

from api.utils.resposta_erro_http import resposta_erro_http


class Questao_service:
    def __init__(self, questao_dao_dependency: Questao_dao):
        print("⬆️ questao_service.__init__()")
        self.__questao_dao = questao_dao_dependency

    _CAMPOS_QUESTAO = [
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

        if self.__questao_dao.campo_existe("enunciado", obj_questao.enunciado):
            raise resposta_erro_http(
                400,
                "Enunciado repetido",
                {"mensagem": f'A questão de enunciado "{obj_questao.enunciado}" já está cadastrada'}
            )

        id_hash = self.__questao_dao.criar(obj_questao)
        return self._formatar_questao(obj_questao, id_hash)

    def consulta(self, filtro) -> list[dict]:
        print("🟣 questao_service.consulta()")
        return self.__questao_dao.consulta(filtro)

    def atualizar(self, json_questao: dict, id_hash: str) -> dict:
        print("🟣 questao_service.atualizar()")

        obj_questao = Questao()
        self._setar_modelo_questao(obj_questao, json_questao)
        obj_questao.id_hash = id_hash

        sucesso = self.__questao_dao.atualizar(obj_questao)
        if not sucesso:
            raise resposta_erro_http(
                400,
                "Questão não existe",
                {"mensagem": "A questão com Id fornecido não existe no banco de dados"}
            )

        return self._formatar_questao(obj_questao, id_hash)

    def excluir(self, id_hash: str) -> bool:
        print("🟣 questao_service.excluir()")
        obj_questao = Questao()
        obj_questao.id_hash = id_hash
        return self.__questao_dao.excluir(obj_questao.id_hash)

    def _setar_modelo_questao(self, obj_questao, json_questao):
        for campo in self._CAMPOS_QUESTAO:
            setattr(obj_questao, campo, json_questao.get(campo))

        dados_professor = json_questao.get("professor")
        professor = Usuario()
        professor.nome = dados_professor.get("nome")
        obj_questao.professor = professor

        if obj_questao.tipo_questao == "Objetiva":
            textos_alternativas = json_questao.get("alternativas")
            if not isinstance(textos_alternativas, list):
                raise TypeError("Alternativas devem ser uma lista")

            alternativas = []
            for texto in textos_alternativas:
                if not isinstance(texto, str):
                    raise TypeError("Cada alternativa deve ser uma string")
                texto = texto.strip()
                if not texto:
                    raise ValueError("Texto da alternativa não pode ser vazio")
                alternativas.append(Alternativa(str(uuid4()), texto))

            obj_questao.alternativas = alternativas

            texto_correto = json_questao.get("alternativa_correta")
            if not isinstance(texto_correto, str):
                raise TypeError("Alternativa correta deve ser uma string")
            texto_correto = texto_correto.strip()

            alternativa_correta = next(
                (
                    alternativa
                    for alternativa in alternativas
                    if alternativa.texto == texto_correto
                ),
                None
            )
            if alternativa_correta is None:
                raise ValueError("Alternativa correta deve estar na lista de alternativas")

            obj_questao.alternativa_correta = alternativa_correta.id
        else:
            obj_questao.numero_linhas = json_questao.get("numero_linhas")

        if "autor" not in json_questao:
            obj_questao.autor = obj_questao.professor.nome
        else:
            obj_questao.autor = json_questao.get("autor")

    def _formatar_questao(self, obj_questao, id_hash):
        formatada = {
            "_id": id_hash,
            "professor": {"nome": obj_questao.professor.nome},
            "assunto": obj_questao.assunto,
            "disciplina": obj_questao.disciplina,
            "tipo_questao": obj_questao.tipo_questao,
            "dificuldade": obj_questao.dificuldade,
            "autor": obj_questao.autor,
            "enunciado": obj_questao.enunciado
        }

        if obj_questao.tipo_questao == "Objetiva":
            formatada["alternativas"] = [
                {"id": alternativa.id, "texto": alternativa.texto}
                for alternativa in obj_questao.alternativas
            ]
            formatada["alternativa_correta"] = obj_questao.alternativa_correta
        else:
            formatada["numero_linhas"] = obj_questao.numero_linhas

        return formatada
