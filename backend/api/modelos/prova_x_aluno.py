class Prova_x_aluno:
    def __init__(self):
        self.__matricula_aluno = None
        self.__id_prova = None
        self.__questoes = None

    @property
    def matricula_aluno(self):
        return self.__matricula_aluno

    @matricula_aluno.setter
    def matricula_aluno(self, value):
        if value is None:
            raise ValueError("Matrícula do aluno nula")

        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError("Matrícula do aluno deve ser int")

        if len(str(value)) != 8:
            raise ValueError("Matrícula deve ter 8 dígitos")

        self.__matricula_aluno = value

    @property
    def id_prova(self):
        return self.__id_prova

    @id_prova.setter
    def id_prova(self, value):
        if value is None:
            raise ValueError("Id da prova nulo")

        if not isinstance(value, str):
            raise TypeError("Id da prova deve ser uma string")

        value = value.strip()
        if not value:
            raise ValueError("Id da prova não pode ser vazio")

        self.__id_prova = value

    @property
    def questoes(self):
        return self.__questoes

    @questoes.setter
    def questoes(self, value):
        if not isinstance(value, list):
            raise TypeError("Questões devem ser uma lista")

        if not value:
            raise ValueError("Informe ao menos uma questão")

        ids_questoes = set()
        questoes_normalizadas = []

        for indice, questao in enumerate(value, start=1):
            if not isinstance(questao, dict):
                raise TypeError(f"A questão {indice} deve ser um objeto")

            id_questao = questao.get("id_questao")
            if not isinstance(id_questao, str):
                raise TypeError(f"O id da questão {indice} deve ser uma string")

            id_questao = id_questao.strip()
            if not id_questao:
                raise ValueError(f"O id da questão {indice} não pode ser vazio")

            if id_questao in ids_questoes:
                raise ValueError("As questões do aluno não podem conter ids repetidos")

            posicao = questao.get("posicao_alternativa_correta")
            if not isinstance(posicao, int) or isinstance(posicao, bool):
                raise TypeError(
                    f"A posição da alternativa correta da questão {indice} deve ser int"
                )

            if posicao not in range(1, 6):
                raise ValueError(
                    f"A posição da alternativa correta da questão {indice} deve variar de 1 a 5"
                )

            ids_questoes.add(id_questao)
            questoes_normalizadas.append({
                "id_questao": id_questao,
                "posicao_alternativa_correta": posicao
            })

        self.__questoes = questoes_normalizadas
