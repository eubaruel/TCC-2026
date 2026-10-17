from api.modelos.usuario import Usuario
from api.modelos.disciplina import Disciplina

class Prova:
    MAX_QUESTOES = 10
    STATUS_EDITAVEIS = ("Aguardando questões", "Em elaboração")
    STATUS_ENVIADA = "Enviada ao pedagógico"
    STATUS_IMPRESSA = "Impressa"

    def __init__(self):
        self.__id_hash = None   
        self.__id_turma = None     #id das turmas as quais farão essa prova
        self.__disciplina = None   #id da disciplina da prova
        self.__professor = None    #objeto professor autor da prova
        self.__status = None       #se a prova foi corrigida ou não
        self.__tipo = None         #provas objetivas
        self.__serie = None        #para qual série essa prova foi feita 
        self.__periodo_letivo = None
        self.__data_de_aplicacao = None 
        self.__questoes = None
        self.__quantidade_questoes = None
    
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
        
        elif isinstance(value,list):
            for turma in value:
                if not isinstance(turma, str):
                    raise TypeError("Cada turma deve ser uma string")
            value = [turma.strip() for turma in value]
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
        if value != "Objetiva":
            raise ValueError("Apenas provas objetivas são permitidas")
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
    def periodo_letivo(self):
        return self.__periodo_letivo

    @periodo_letivo.setter
    def periodo_letivo(self, value):
        if value is None:
            raise ValueError("Período letivo nulo")
        if not isinstance(value, str):
            raise TypeError("Período letivo deve ser string")
        value = value.strip()
        self.__periodo_letivo = value


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
    def quantidade_questoes(self):
        return self.__quantidade_questoes

    @quantidade_questoes.setter
    def quantidade_questoes(self, value):
        if type(value) is not int:
            raise TypeError("Quantidade de questões deve ser um inteiro")
        if not 2 <= value <= self.MAX_QUESTOES:
            raise ValueError(f"Quantidade de questões deve ser de 2 a {self.MAX_QUESTOES}")
        self.__quantidade_questoes = value

    @property
    def questoes(self):
        return self.__questoes

    @questoes.setter
    def questoes(self, value):
        if value is None:
            raise ValueError("Questões nulas")
        if not isinstance(value, list):
            raise TypeError("Questões devem ser uma lista")
        for id_questao in value:
            if not isinstance(id_questao, str):
                raise TypeError("Cada questão da prova deve ser representada por um id")
        self.__questoes = value


