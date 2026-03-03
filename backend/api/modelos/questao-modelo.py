import re     #Biblioteca para o uso de regex

class questao_modelo:
    def __init__(self):

        self.__id_questao = None
        #id do professor que cadastrou a questão no sistema
        self.__id_professor = None
        self.__assunto = None
        self.__disciplina = None
        self.__palavras_chave = None
        #se é objetiva ou dissertativa
        self.__tipo_questao = None
        self.__dificuldade = None 
        #Ex: Professor, Universidades, etc.
        self.__autor = None 
        self.__alternativas = None #lista
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
    def assunto(self):
        return self.__assunto
    
    @assunto.setter
    def assunto(self,value):
        if value is None:
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
        if value is None:
            raise ValueError("Disciplina(as) nula")
        if not isinstance(value, list):
            raise TypeError("Diciplina(as) devem ser uma lista")
        
        palavras_normalizadas = []

        for palavra in value:
            if not isinstance(palavra, str):
                raise TypeError("Cada palavra-chave deve ser uma string")

            palavra = palavra.strip().lower()

            if len(palavra) < 2:
                raise ValueError("Palavra-chave muito curta")

            palavras_normalizadas.append(palavra)
        
        self.__disciplina = palavras_normalizadas[:]

    @property
    def palavras_chave(self):
        return self.__palavras_chave
    
    @palavras_chave.setter
    def palavras_chave(self,value):
        if value is None:
            raise ValueError("Palavra(as) chave nula")
        if not isinstance(value, list):
            raise TypeError("Palavras-chave devem ser uma lista")
        
        palavras_normalizadas = []

        for palavra in value:
            if not isinstance(palavra, str):
                raise TypeError("Cada palavra-chave deve ser uma string")

            palavra = palavra.strip().lower()

            if len(palavra) < 2:
                raise ValueError("Palavra-chave muito curta")

            palavras_normalizadas.append(palavra)
        
        self.__palavras_chave = palavras_normalizadas[:]

    @property
    def tipo_questao(self):
        return self.__tipo_questao
    
    @tipo_questao.setter
    def tipo_questao(self,value):
        if value is None:
            raise ValueError("Tipo da questão nulo")
        if not isinstance(value,str):
            raise TypeError("Tipo da questão deve ser string")
        #FALTA AS REGRAS DE NEGÓCIO
        #
        #
        #
        #
        self.__tipo_questao = value

    @property
    def dificuldade(self):
        return self.__dificuldade

    @dificuldade.setter
    def dificuldade(self, value):
        if value is None:
            raise ValueError("Dificuldade nula")
        if not isinstance(value, str):
            raise TypeError("Dificuldade deve ser str")
        #FALTA AS REGRAS DE NEGÓCIO
        #
        #
        #
        #
        self.__dificuldade = value


    @property
    def autor(self):
        return self.__autor

    @autor.setter
    def autor(self, value):
        if value is None:
            raise ValueError("Autor nulo")
        if not isinstance(value, str):
            raise TypeError("Autor deve ser str")
        #FALTA AS REGRAS DE NEGÓCIO
        #
        #
        #
        #
        self.__autor = value


    @property
    def alternativas(self):
        return self.__alternativas

    @alternativas.setter
    def alternativas(self, value):
        if value is None:
            raise ValueError("Alternativas nula")
        if not isinstance(value, list):
            raise TypeError("Alternativas deve ser list")
        #FALTA AS REGRAS DE NEGÓCIO
        #
        #
        #
        #
        self.__alternativas = value


    @property
    def correta(self):
        return self.__correta

    @correta.setter
    def correta(self, value):
        if value is None:
            raise ValueError("Correta nula")
        if not isinstance(value, str):
            raise TypeError("Correta deve ser str")
        #FALTA AS REGRAS DE NEGÓCIO
        #
        #
        #
        #
        self.__correta = value
            
        
                