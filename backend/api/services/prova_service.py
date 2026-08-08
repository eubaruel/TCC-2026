from api.modelos.prova import Prova
from api.modelos.disciplina import Disciplina
from api.modelos.questao import Questao
from api.modelos.usuario import Usuario
from api.DAOs.prova_dao import Prova_dao

from api.utils.resposta_erro_http import resposta_erro_http

class Prova_service:
    def __init__(self, prova_dao_dependency: Prova_dao):
        print("⬆️ prova_service.__init__()")
        self.__prova_dao = prova_dao_dependency

    _CAMPOS_PROVA = [
        "id_turma",
        "status",
        "tipo",
        "serie",
        "bimestre",
        "data_de_aplicacao"
    ]


    def criar (self, json_prova: dict):
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
                {"mensagem":f'A prova com Id fornecido não existe no banco de dados'}
            )

        return self.__prova_dao.atualizar(obj_prova)
    

    def excluir(self, id_hash: str) -> bool:
        print("🟣 prova_service.excluir()")
        obj_prova = Prova()
        obj_prova.id_hash = id_hash
        return self.__prova_dao.excluir(obj_prova.id_hash)

    def _setar_modelo_prova(self,obj_prova,json_prova):
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

        obj_prova.questoes = self._validar_e_normalizar_questoes(
            json_prova.get("questoes"),
            obj_prova
        )

    def _validar_e_normalizar_questoes(self, questoes, obj_prova):
        if not isinstance(questoes, list):
            raise resposta_erro_http(
                400,
                "Questões inválidas",
                {"mensagem": "O campo 'questoes' deve ser uma lista de objetos completos"}
            )

        if len(questoes) < 5:
            raise resposta_erro_http(
                400,
                "Número de questões insuficiente",
                {"mensagem": "A prova deve possuir ao menos cinco questões"}
            )

        referencias_disciplina = {
            obj_prova.disciplina.codigo_disciplina.strip().lower(),
            obj_prova.disciplina.nome_disciplina.strip().lower()
        }

        normalizadas = []
        enunciados = set()
        for indice, dados_questao in enumerate(questoes, start=1):
            if not isinstance(dados_questao, dict):
                raise resposta_erro_http(
                    400,
                    "Questão inválida",
                    {"mensagem": f"A questão {indice} deve ser um objeto completo"}
                )

            questao = self._criar_modelo_questao(dados_questao)
            if questao.tipo_questao != obj_prova.tipo:
                raise resposta_erro_http(
                    400,
                    "Tipo de questão incompatível",
                    {"mensagem": f"A questão {indice} não é do tipo {obj_prova.tipo}"}
                )

            disciplinas_questao = {
                str(valor).strip().lower()
                for valor in questao.disciplina
            }
            if not referencias_disciplina.intersection(disciplinas_questao):
                raise resposta_erro_http(
                    400,
                    "Disciplina incompatível",
                    {"mensagem": f"A questão {indice} não pertence à disciplina da prova"}
                )

            chave_enunciado = questao.enunciado.strip().casefold()
            if chave_enunciado in enunciados:
                raise resposta_erro_http(
                    400,
                    "Questões repetidas",
                    {"mensagem": "A prova não pode conter questões com o mesmo enunciado"}
                )
            enunciados.add(chave_enunciado)
            normalizadas.append(self._formatar_questao(questao))

        return normalizadas

    def _criar_modelo_questao(self, dados):
        questao = Questao()
        dados_professor = dados.get("professor")
        if not isinstance(dados_professor, dict):
            raise ValueError("Professor da questão deve ser um objeto")

        professor = Usuario()
        professor.nome = dados_professor.get("nome")
        questao.professor = professor
        questao.assunto = dados.get("assunto")
        questao.disciplina = dados.get("disciplina")
        questao.tipo_questao = dados.get("tipo_questao")
        questao.dificuldade = dados.get("dificuldade")
        questao.autor = dados.get("autor", professor.nome)
        questao.enunciado = dados.get("enunciado")

        if questao.tipo_questao == "Objetiva":
            questao.alternativas = dados.get("alternativas")
            questao.alternativa_correta = dados.get("alternativa_correta")
        else:
            questao.numero_linhas = dados.get("numero_linhas")

        return questao

    def _formatar_questao(self, questao):
        formatada = {
            "professor": {"nome": questao.professor.nome},
            "assunto": questao.assunto,
            "disciplina": questao.disciplina,
            "tipo_questao": questao.tipo_questao,
            "dificuldade": questao.dificuldade,
            "autor": questao.autor,
            "enunciado": questao.enunciado
        }

        if questao.tipo_questao == "Objetiva":
            formatada["alternativas"] = questao.alternativas
            formatada["alternativa_correta"] = questao.alternativa_correta
        else:
            formatada["numero_linhas"] = questao.numero_linhas

        return formatada
