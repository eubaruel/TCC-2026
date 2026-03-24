import re
from aluno import Aluno

class Responsavel:
    def __init__(self):
        
        self.__id_hash = None
        self.__nome_responsavel = None
        self.__email_responsavel = None
        self.__aluno = None
        self.__telefone_responsavel = None

    @property
    def id_hash(self):
        return self.__id_hash
    
    @id_hash.setter
    def id_hash(self, value):
        if value is None:
            raise ValueError("Id hash nulo")
        
        if not isinstance(value, str):
            raise TypeError("Id deve ser uma string")
        
        self.__id_hash = value
        
    @property
    def nome_responsavel(self):
        return self.__nome_responsavel

    @nome_responsavel.setter
    def nome_responsavel(self, value):
        if value is None:
            raise ValueError("Nome responsável nulo")

        if not isinstance(value, str):
            raise TypeError("Nome responsável deve ser uma string")

        value = value.strip().title()
        
        if len(value) < 5:
            raise ValueError("Nome do responsável deve ter ao menos 5 caracteres")

        if len(value.split()) < 2:
            raise ValueError("Nome do responsável deve ter ao menos um sobrenome")
        
        for nome in value.split(): 
            if len(nome) < 2:
                raise ValueError("Cada parte do nome deve conter ao menos 2 caracteres")
        
        self.__nome_responsavel = value

    
    @property
    def email_responsavel(self):
        return self.__email_responsavel

    @email_responsavel.setter
    def email_responsavel(self, value):
        if value != None:
            if not isinstance(value, str):
                raise TypeError("Email responsável deve ser uma string")

            value = value.strip()

            if len(value) not in range(5,151):
                raise ValueError("Email deve conter de 5 a 150 caracteres")
            
            padrao = "^[a-zA-Z0-9][a-zA-Z0-9._%+-]{0,63}@[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

            if not re.match(padrao,value):
                raise ValueError("Email inválido")
            
            self.__email_responsavel = value

    @property
    def aluno(self):
        return self.__aluno
    
    @aluno.setter
    def aluno(self, value):
        if not isinstance(value, Aluno):
            raise ValueError("Aluno deve ser uma instância válida")
        self.__aluno = value
    
    @property
    def telefone_responsavel(self):
        return self.__telefone_responsavel
    
    @telefone_responsavel.setter
    def telefone_responsavel(self, value):
        if value is None:
            raise ValueError("Telefone do responsável nulo")

        if not isinstance(value, str):
            raise TypeError("Telefone do responsável deve ser uma string")
        
        value = ''.join(filter(str.isdigit, str(value)))

        if len(value) < 10:
            raise ValueError("Telefone deve ter ao menos 10 caracteres")

        self.__telefone_responsavel = value