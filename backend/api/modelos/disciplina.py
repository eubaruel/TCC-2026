from api.modelos.usuario import Usuario

class Disciplina:
    def __init__(self):

        self.__codigo_disciplina = None #string
        self.__nome_disciplina = None #string
        self.__professor = None #objeto
        self.__turma = None #string
        self.__alunos = None #lista com matrículas

    @property
    def id_hash(self):
        return self.__id_hash

    @id_hash.setter
    def id_hash(self, value):
        if value is None:
            raise ValueError("Id hash nulo")

        if not isinstance(value, str):
            raise TypeError("Id hash deve ser uma string")

        value = value.strip()
        self.__id_hash = value


    @property
    def professor(self):
        return self.__professor

    @professor.setter
    def professor(self, value):
        if not isinstance(value, Usuario):
            raise TypeError("Professor deve ser uma instância válida")

        self.__professor = value


    @property
    def nome_disciplina(self):
        return self.__nome_disciplina

    @nome_disciplina.setter
    def nome_disciplina(self, value):
        if value is None:
            raise ValueError("Nome da disciplina nulo")

        if not isinstance(value, str):
            raise TypeError("Nome da disciplina deve ser uma string")

        value = value.strip().title()

        if len(value) < 3:
            raise ValueError("Nome da disciplina deve ter ao menos 3 caracteres")   

        self.__nome_disciplina = value


    @property
    def codigo_disciplina(self):
        return self.__codigo_disciplina

    @codigo_disciplina.setter
    def codigo_disciplina(self, value):
        if value is None:
            raise ValueError("Código da disciplina nulo")

        if not isinstance(value, str):
            raise TypeError("Código da disciplina deve ser uma string")

        value = value.strip()
        self.__codigo_disciplina = value


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
    def alunos(self):
        return self.__alunos

    @alunos.setter
    def alunos(self, value):
        if value is None:
            raise ValueError("Alunos nulo")

        if not isinstance(value, list):
            raise TypeError("Alunos deve ser uma lista")
        
        if len(value) == 0:
            raise ValueError("Lista de alunos não pode ser vazia")
        
        for matricula in value:
            if not isinstance(matricula, int):
                raise TypeError("Matrícula do aluno deve ser int")
        
            if not len(str(matricula)) == 8:
                raise ValueError("Matrícula deve ter 8 dígitos")

        self.__alunos = value