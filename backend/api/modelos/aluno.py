import re

class Aluno:
    def __init__(self):
        
        self.__id_hash = None #string
        self.__matricula_aluno = None #int
        self.__nome_aluno = None #string
        self.__turma = None #string
        self.__serie = None #int
        self.__situacao = None #string
        self.__email_aluno = None #string

    @property
    def id_hash(self):
        return self.__id_hash

    @id_hash.setter
    def id_hash(self, value):
        if value is None:
            raise ValueError("Id nulo")

        if not isinstance(value, str):
            raise TypeError("Id deve ser uma string")

        value = value.strip()
        self.__id_hash = value


    @property
    def matricula_aluno(self):
        return self.__matricula_aluno

    @matricula_aluno.setter
    def matricula_aluno(self, value):
        if value is None:
            raise ValueError("Matrícula do aluno nula")

        if not isinstance(value, int):
            raise TypeError("Matrícula do aluno deve ser int")
        
        if not len(str(value)) == 8:
            raise ValueError("Matrícula deve ter 8 dígitos")

        self.__matricula_aluno = value


    @property
    def nome_aluno(self):
        return self.__nome_aluno

    @nome_aluno.setter
    def nome_aluno(self, value):
        if value is None:
            raise ValueError("Nome do aluno nulo")

        if not isinstance(value, str):
            raise TypeError("Nome do aluno deve ser uma string")

        value = value.strip().title()
        
        if len(value) < 5:
            raise ValueError("Nome do aluno deve ter ao menos 5 caracteres")

        if len(value.split()) < 2:
            raise ValueError("Nome do aluno deve ter ao menos um sobrenome")
        
        for nome in value.split(): 
            if len(nome) < 3:
                raise ValueError("Cada parte do nome deve conter ao menos 3 caracteres")
        
        self.__nome_aluno = value


    @property
    def turma(self):
        return self.__turma

    @turma.setter
    def turma(self, value):
        if value is None:
            raise ValueError("Turma nula")

        if not isinstance(value, str):
            raise TypeError("Turma deve ser uma string")

        value = value.strip()

        if len(value) < 10:
            raise ValueError("Turma deve ter ao menos 10 caracteres")
        self.__turma = value


    @property
    def serie(self):
        return self.__serie

    @serie.setter
    def serie(self, value):
        if value is None:
            raise ValueError("Série nula")

        if not isinstance(value, int):
            raise TypeError("Série deve ser int")
        
        if value <= 0:
            raise ValueError("Série deve ser maior que 0")
        
        self.__serie = value


    @property
    def situacao(self):
        return self.__situacao

    @situacao.setter
    def situacao(self, value):
        if value is None:
            raise ValueError("Situação do aluno nula")

        if not isinstance(value, str):
            raise TypeError("Situação do aluno deve ser uma string")
        
        if not value.isalpha():
            raise ValueError("Situação do aluno não pode conter números")

        self.__situacao = value


    @property
    def email_aluno(self):
        return self.__email_aluno

    @email_aluno.setter
    def email_aluno(self, value):
        if value != None:

            if not isinstance(value, str):
                raise TypeError("Email do aluno deve ser uma string")

            value = value.strip()

            if len(value) not in range(5,151):
                raise ValueError("Email deve conter de 5 a 150 caracteres")
            
            padrao = "^[a-zA-Z0-9][a-zA-Z0-9._%+-]{0,63}@[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

            if not re.match(padrao,value):
                raise ValueError("Email inválido")

            self.__email_aluno = value