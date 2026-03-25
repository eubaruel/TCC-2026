import re

class Professor:
    def __init__(self):
        self.__id_hash = None #string
        self.__registro_professor = None #int
        self.__nome_professor = None #string
        self.__email_professor = None #string

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
    def registro_professor(self):
        return self.__registro_professor

    @registro_professor.setter
    def registro_professor(self, value):
        if value is None:
            raise ValueError("Registro do professor nulo")

        if not isinstance(value, int):
            raise TypeError("Registro do professor deve ser um int")

        self.__registro_professor = value


    @property
    def nome_professor(self):
        return self.__nome_professor

    @nome_professor.setter
    def nome_professor(self, value):
        if value is None:
            raise ValueError("Nome do professor nulo")

        if not isinstance(value, str):
            raise TypeError("Nome do professor deve ser uma string")

        value = value.strip().title()
        
        if len(value) < 5:
            raise ValueError("Nome do professor deve ter ao menos 5 caracteres")

        if len(value.split()) < 2:
            raise ValueError("Nome do professor deve ter ao menos um sobrenome")
        
        for nome in value.split(): 
            if len(nome) < 3:
                raise ValueError("Cada parte do nome deve conter ao menos 3 caracteres")

        self.__nome_professor = value


    @property
    def email_professor(self):
        return self.__email_professor

    @email_professor.setter
    def email_professor(self, value):
        if value != None:
            
            if not isinstance(value, str):
                raise TypeError("Email do professor deve ser uma string")

            value = value.strip()

            if len(value) not in range(5,151):
                raise ValueError("Email deve conter de 5 a 150 caracteres")
            
            padrao = "^[a-zA-Z0-9][a-zA-Z0-9._%+-]{0,63}@[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

            if not re.match(padrao,value):
                raise ValueError("Email inválido")
            
            self.__email_professor = value.lower()

    @property
    def ativo(self):
        return self.__ativo
    
    @ativo.setter
    def ativo(self,value):
        if value is None:
            raise ValueError("Ativo nulo")
        
        if not isinstance(value,bool):
            raise TypeError("Ativo deve ser booleano")
        
        self.__ativo = value