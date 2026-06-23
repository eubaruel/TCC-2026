from functools import wraps
from flask import request
from api.utils.resposta_erro_http import resposta_erro_http

class Prova_middleware:
    def validar_body(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print("🔷 prova_middleware.validar_body()")

            body = request.get_json()

            if not body or "prova" not in body:
                raise resposta_erro_http(
                    400,
                    "Erro na validação de dados",
                    {"mensagem": "O campo 'prova' é obrigatório!"}
                )

            prova = body["prova"]

            campos_obrigatorios = [
                "id_turma",
                "professor",
                "disciplina",
                "status",
                "tipo",
                "serie",
                "bimestre",
                "data_de_aplicacao",
                "questoes"
            ]

            campos_obrigatorios_professor = [
                "nome"
            ]

            campos_obrigatorios_disciplina = [
                "codigo_disciplina",
                "nome_disciplina"
            ]


            for campo in campos_obrigatorios:
                if campo not in prova:
                    raise resposta_erro_http(
                        400,
                        "Erro na validação de dados",
                        {"mensagem": f"O campo '{campo}' é obrigatório!"}
                    )

            professor = prova["professor"]
            disciplina = prova["disciplina"]

            for campo_professor in campos_obrigatorios_professor:
                if campo_professor not in professor:
                    raise resposta_erro_http(
                        400,
                        "Erro na validação de dados",
                        {
                            "mensagem":
                            f"O campo '{campo_professor}' do professor é obrigatório!"
                        }
                    )

            for campo_disciplina in campos_obrigatorios_disciplina:
                if campo_disciplina not in disciplina:
                    raise resposta_erro_http(
                        400,
                        "Erro na validação de dados",
                        {
                            "mensagem":
                            f"O campo '{campo_disciplina}' da disciplina é obrigatório!"
                        }
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