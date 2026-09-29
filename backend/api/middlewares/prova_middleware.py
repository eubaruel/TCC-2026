from functools import wraps

from flask import request

from api.utils.resposta_erro_http import resposta_erro_http


class Prova_middleware:
    _CAMPOS_CRIACAO = [
        "id_turma",
        "professor",
        "disciplina",
        "tipo",
        "serie",
        "bimestre",
        "data_de_aplicacao"
    ]

    _CAMPOS_GERENCIADOS_PELA_API = {
        "_id",
        "ativo",
        "questoes",
        "status"
    }

    def validar_criar_prova(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("🔷 prova_middleware.validar_criar_prova()")

            body = request.get_json(silent=True)
            if not isinstance(body, dict) or "prova" not in body:
                raise resposta_erro_http(
                    400,
                    "Erro na validação de dados",
                    {"mensagem": "O campo 'prova' é obrigatório!"}
                )

            prova = body["prova"]
            if not isinstance(prova, dict):
                raise resposta_erro_http(
                    400,
                    "Erro na validação de dados",
                    {"mensagem": "O campo 'prova' deve ser um objeto!"}
                )

            for campo in self._CAMPOS_CRIACAO:
                if campo not in prova:
                    raise resposta_erro_http(
                        400,
                        "Erro na validação de dados",
                        {"mensagem": f"O campo '{campo}' é obrigatório!"}
                    )

            campos_proibidos = sorted(
                self._CAMPOS_GERENCIADOS_PELA_API.intersection(prova)
            )
            if campos_proibidos:
                raise resposta_erro_http(
                    400,
                    "Erro na validação de dados",
                    {
                        "mensagem":
                        "Campos gerenciados pela API não devem ser enviados: "
                        + ", ".join(campos_proibidos)
                    }
                )

            professor = prova["professor"]
            if not isinstance(professor, dict):
                raise resposta_erro_http(
                    400,
                    "Erro na validação de dados",
                    {"mensagem": "O campo 'professor' deve ser um objeto!"}
                )

            for campo in ["registro", "nome"]:
                if campo not in professor:
                    raise resposta_erro_http(
                        400,
                        "Erro na validação de dados",
                        {
                            "mensagem":
                            f"O campo '{campo}' do professor é obrigatório!"
                        }
                    )

            disciplina = prova["disciplina"]
            if not isinstance(disciplina, dict):
                raise resposta_erro_http(
                    400,
                    "Erro na validação de dados",
                    {"mensagem": "O campo 'disciplina' deve ser um objeto!"}
                )

            for campo in ["codigo_disciplina", "nome_disciplina"]:
                if campo not in disciplina:
                    raise resposta_erro_http(
                        400,
                        "Erro na validação de dados",
                        {
                            "mensagem":
                            f"O campo '{campo}' da disciplina é obrigatório!"
                        }
                    )

            return f(*args, **kwargs)

        return decorated_function

    def validar_adicionar_questoes(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("🔷 prova_middleware.validar_adicionar_questoes()")

            body = request.get_json(silent=True)
            if not isinstance(body, dict) or "prova" not in body:
                raise resposta_erro_http(
                    400,
                    "Erro na validação de dados",
                    {"mensagem": "O campo 'prova' é obrigatório!"}
                )

            prova = body["prova"]
            if not isinstance(prova, dict):
                raise resposta_erro_http(
                    400,
                    "Erro na validação de dados",
                    {"mensagem": "O campo 'prova' deve ser um objeto!"}
                )

            if "questoes" not in prova:
                raise resposta_erro_http(
                    400,
                    "Erro na validação de dados",
                    {"mensagem": "O campo 'questoes' é obrigatório!"}
                )

            if not isinstance(prova["questoes"], list):
                raise resposta_erro_http(
                    400,
                    "Questões inválidas",
                    {"mensagem": "O campo 'questoes' deve ser uma lista de ids"}
                )

            return f(*args, **kwargs)

        return decorated_function

    def validar_id_prova(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("🔷 prova_middleware.validar_id()")

            if "_id" not in kwargs:
                raise resposta_erro_http(
                    400,
                    "Erro na validação de dados",
                    {"mensagem": "O parâmetro '_id' é obrigatório!"}
                )

            return f(*args, **kwargs)

        return decorated_function
