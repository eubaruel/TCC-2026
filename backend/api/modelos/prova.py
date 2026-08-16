from api.modelos.usuario import Usuario
from api.modelos.disciplina import Disciplina

class Prova:
    def __init__(self):
        self.__id_hash = None   
        self.__id_turma = None     #id das turmas as quais farão essa prova
        self.__disciplina = None   #id da disciplina da prova
        self.__professor = None    #objeto professor autor da prova
        self.__status = None       #se a prova foi corrigida ou não
        self.__tipo = None         #se é objetiva ou dissertativa
        self.__serie = None        #para qual série essa prova foi feita 
        self.__bimestre = None    
        self.__data_de_aplicacao = None 
        self.__questoes = None
    
    @property
    def id_hash(self):
        return self.__id_hash

    @id_hash.setter
    def id_hash(self, value):
        if value is None:
            raise ValueError("Id_hash da prova nulo")
        
        if not isinstance(value, str):
            raise TypeError("Id da prova deve ser string")
        self.__id_hash = value


    @property
    def id_turma(self):
        return self.__id_turma

    @id_turma.setter
    def id_turma(self, value):
        if value is None:
            raise ValueError("Id da turma nulo")
        
        if isinstance(value,str):
            value = value.strip()        
            if len(value) < 10:
                raise ValueError("Turma deve ter ao menos 10 caracteres")
        
        elif isinstance(value,list):
            for turma in value:
                if not isinstance(turma, str):
                    raise TypeError("Cada turma deve ser uma string")
            value = [turma.strip() for turma in value]
            for turma in value:
                if len(turma) < 10:
                    raise ValueError("Turma deve ter ao menos 10 caracteres")
        else:
            raise TypeError("Id da turma deve ser lista ou string")
        self.__id_turma = value


    @property
    def disciplina(self):
        return self.__disciplina

    @disciplina.setter
    def disciplina(self, value):
        if not isinstance(value, Disciplina):
            raise ValueError("Disciplina deve ser uma instância válida")
        self.__disciplina = value

    
    @property
    def professor(self):
        return self.__professor

    @professor.setter
    def professor(self, value):
        if not isinstance(value, Usuario):
            raise ValueError("Professor deve ser uma instância válida")
        self.__professor = value


    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        if value is None:
            raise ValueError("Status nulo")
        if not isinstance(value, str):
            raise TypeError("Status deve ser string")
        value = value.strip()
        if value not in ["Corrigida", "Não Corrigida"]:
            raise ValueError("Status inválido")
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
        value = value.strip().title()
        if value not in ["Objetiva", "Dissertativa"]:
            raise ValueError("Tipo inválido")
        self.__tipo = value


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
            raise ValueError("Série deve ser maior que zero")
        self.__serie = value


    @property
    def bimestre(self):
        return self.__bimestre

    @bimestre.setter
    def bimestre(self, value):
        if value is None:
            raise ValueError("Bimestre nulo")
        if not isinstance(value, str):
            raise TypeError("Bimestre deve ser string")
        value = value.strip()
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
        value = value.strip()
        self.__data_de_aplicacao = value


    @property
    def questoes(self):
        return self.__questoes

    @questoes.setter
    def questoes(self, value):
        if value is None:
            raise ValueError("Questões nulas")
        if not isinstance(value, list):
            raise TypeError("Questões devem ser uma lista")
        if len(value) < 5:
            raise ValueError("A prova deve possuir ao menos cinco questões")
        for id_questao in value:
            if not isinstance(id_questao, str):
                raise TypeError("Cada questão da prova deve ser representada por um id")
        self.__questoes = value


