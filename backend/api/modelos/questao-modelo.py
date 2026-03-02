import re

class Questao:
    def __init__(self):

        self.__id_questao = None
        #id do professor que cadastrou a questão no sistema
        self.__id_professor = None
        self.__assunto = None
        self.__disciplina = None
        self.__palavras_chave = None
        #se é objetiva ou dissertativa
        self.__tipo_questao = None
        self.__dificulade = None
        #Ex: Professor, Universidades, etc.
        self.__autor = None
        self.__alternativas = None
        self.__correta = None

    @property
    def id_questao(self):
        return self.__id_questao
    
    @id_questao.setter
    def id_questao(self,value):
        try:
            parsed = int(value)
        except(ValueError, TypeError):
            raise ValueError("Id deve ser um número inteiro")
        
        if parsed <= 0:
            raise ValueError("Id deve ser um número maior que zero")
        
        self.__id_questao = parsed

    
    #CRIA O DO GET/SET DO ID PROFESSOR
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
    def assunto(self):
        return self.__assunto
    
    @assunto.setter
    def assunto(self,value):
        if not value:
            raise ValueError("Assunto nulo")
        parsed = str(value)
        parsed = parsed.strip().title()
        #FALTA AS REGRAS DE NEGÓCIO
        #
        #
        #
        #
        self.__assunto = parsed

    @property
    def disciplina(self):
        return self.__disciplina
    
    @disciplina.setter
    def disciplina(self,value):
        if not value:
            raise ValueError("Disciplina nula")
        parsed = str(value)
        parsed = parsed.strip().capitalize()
        #FALTA AS REGRAS DE NEGÓCIO
        #
        #
        #
        #

    @property
    def palavras_chave(self):
        return self.__palavras_chave
    
    @palavras_chave.setter
    def palavras_chave(self,value):
        if not value:
            raise ValueError("Palavra(as) chave nula")
        if not isinstance(value, list):
            raise ValueError("Palavras-chave devem ser uma lista")
        
        palavras_normalizadas = []

        for palavra in value:
            if not isinstance(palavra, str):
                raise TypeError("Cada palavra-chave deve ser uma string")

            palavra = palavra.strip().lower()

            if len(palavra) < 2:
                raise ValueError("Palavra-chave muito curta")

            palavras_normalizadas.append(palavra)
            