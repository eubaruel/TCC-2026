import re     #Biblioteca para o uso de regex

class prova_modelo:
    def __init__(self):
        
        self.__id_prova = None
        #id das turmas as quais farão essa prova
        self.__id_turma = None 
        self.__id_disciplina = None 
        self.__id_professor = None 
        self.__status = None 
        #se é objetiva ou dissertativa
        self.__tipo = None 
        #para qual ano essa prova foi feita
        self.__ano = None 
        self.__bimestre = None 
        self.__data_de_aplicacao = None 
        #id das questões que contém a determinada prova
        self.__id_questao = None 

    @property
    def id_prova(self):
        return self.__id_prova

    @id_prova.setter
    def id_prova(self, value):
        if value is None:
            raise ValueError("Id da prova nulo")
        if not isinstance(value, int):
            raise TypeError("Id da prova deve ser inteiro")
        #FALTA AS REGRAS DE NEGÓCIO
        #
        #
        #
        #
        self.__id_prova = value


    @property
    def id_turma(self):
        return self.__id_turma

    @id_turma.setter
    def id_turma(self, value):
        if value is None:
            raise ValueError("Id da turma nulo")
        if not isinstance(value, list):
            raise TypeError("Id da turma deve ser lista")
        #FALTA AS REGRAS DE NEGÓCIO
        #
        #
        #
        #
        self.__id_turma = value


    @property
    def id_disciplina(self):
        return self.__id_disciplina

    @id_disciplina.setter
    def id_disciplina(self, value):
        if value is None:
            raise ValueError("Id da disciplina nulo")
        if not isinstance(value, int):
            raise TypeError("Id da disciplina deve ser inteiro")
        #FALTA AS REGRAS DE NEGÓCIO
        #
        #
        #
        #
        self.__id_disciplina = value

    #GET/SET DO ID PROFESSOR
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #


    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        if value is None:
            raise ValueError("Status nulo")
        if not isinstance(value, str):
            raise TypeError("Status deve ser string")
        #FALTA AS REGRAS DE NEGÓCIO
        #
        #
        #
        #
        self.__status = value


    @property
    def tipo(self):
        return self.__tipo

    @tipo.setter
    def tipo(self, value):
        if value is None:
            raise ValueError("Tipo nulo")
        if not isinstance(value, str):
            raise TypeError("Tipo deve ser string")
        #FALTA AS REGRAS DE NEGÓCIO
        #
        #
        #
        #
        self.__tipo = value


    @property
    def ano(self):
        return self.__ano

    @ano.setter
    def ano(self, value):
        if value is None:
            raise ValueError("Ano nulo")
        if not isinstance(value, str):
            raise TypeError("Ano deve ser string")
        #FALTA AS REGRAS DE NEGÓCIO
        #
        #
        #
        #
        self.__ano = value


    @property
    def bimestre(self):
        return self.__bimestre

    @bimestre.setter
    def bimestre(self, value):
        if value is None:
            raise ValueError("Bimestre nulo")
        if not isinstance(value, str):
            raise TypeError("Bimestre deve ser string")
        #FALTA AS REGRAS DE NEGÓCIO
        #
        #
        #
        #
        self.__bimestre = value


    @property
    def data_de_aplicacao(self):
        return self.__data_de_aplicacao

    @data_de_aplicacao.setter
    def data_de_aplicacao(self, value):
        if value is None:
            raise ValueError("Data de aplicação nula")
        if not isinstance(value, str):
            raise TypeError("Data de aplicação deve ser string")
        #FALTA AS REGRAS DE NEGÓCIO
        #
        #
        #
        #
        self.__data_de_aplicacao = value


    @property
    def id_questao(self):
        return self.__id_questao

    @id_questao.setter
    def id_questao(self, value):
        if value is None:
            raise ValueError("Id da questão nulo")
        if not isinstance(value, list):
            raise TypeError("Id da questão deve ser lista")
        #FALTA AS REGRAS DE NEGÓCIO
        #
        #
        #
        #
        self.__id_questao = value

        

