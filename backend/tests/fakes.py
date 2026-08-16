from copy import deepcopy


class FakeAlunoDao:
    def __init__(self):
        self.documentos = {}
        self.importacoes = []

    def set_doc(self, aluno):
        return {
            "matricula_aluno": aluno.matricula_aluno,
            "nome_aluno": aluno.nome_aluno,
            "turma": aluno.turma,
            "serie": aluno.serie,
            "situacao": aluno.situacao,
            "email_aluno": aluno.email_aluno,
            "ativo": aluno.ativo,
        }

    def campo_existe(self, campo, valor):
        return any(doc.get(campo) == valor for doc in self.documentos.values())

    def criar(self, aluno):
        doc = self.set_doc(aluno)
        self.documentos[aluno.matricula_aluno] = doc
        return True

    def importar_excel(self, docs):
        criados = 0
        atualizados = 0
        for doc in docs:
            matricula = doc["matricula_aluno"]
            if matricula in self.documentos:
                atualizados += 1
            else:
                criados += 1
            self.documentos[matricula] = deepcopy(doc)
        self.importacoes.append(deepcopy(docs))
        return {
            "processados": len(docs),
            "criados": criados,
            "atualizados": atualizados,
        }

    def consulta(self, filtro=None):
        filtro = filtro or {}
        resultado = []
        for doc in self.documentos.values():
            if all(doc.get(chave) == valor for chave, valor in filtro.items()):
                seguro = deepcopy(doc)
                seguro.pop("email_aluno", None)
                resultado.append(seguro)
        return resultado

    def atualizar(self, aluno):
        if aluno.matricula_aluno not in self.documentos:
            return False
        self.documentos[aluno.matricula_aluno] = self.set_doc(aluno)
        return True

    def excluir(self, matricula):
        if matricula not in self.documentos or not self.documentos[matricula]["ativo"]:
            return False
        self.documentos[matricula]["ativo"] = False
        return True


class FakeUsuarioDao:
    def __init__(self):
        self.documentos = {}

    def set_doc(self, usuario):
        return {
            "nome": usuario.nome,
            "email": usuario.email,
            "role": usuario.role,
            "ativo": usuario.ativo,
        }

    def campo_existe(self, campo, valor):
        return any(doc.get(campo) == valor for doc in self.documentos.values())

    def criar(self, usuario):
        doc = self.set_doc(usuario)
        doc["registro"] = usuario.registro
        doc["senha"] = usuario.senha
        self.documentos[usuario.registro] = doc
        return True

    def login(self, usuario):
        doc = self.documentos.get(usuario.registro)
        if not doc or not doc["ativo"]:
            return None
        return deepcopy(doc)

    def consulta(self, filtro=None):
        filtro = filtro or {}
        resultado = []
        for doc in self.documentos.values():
            if all(doc.get(chave) == valor for chave, valor in filtro.items()):
                seguro = deepcopy(doc)
                seguro.pop("senha", None)
                resultado.append(seguro)
        return resultado

    def atualizar(self, usuario):
        doc = self.documentos.get(usuario.registro)
        if not doc:
            return False
        senha = doc["senha"]
        doc.update(self.set_doc(usuario))
        doc["senha"] = senha
        return True

    def excluir(self, registro):
        doc = self.documentos.get(registro)
        if not doc or not doc["ativo"]:
            return False
        doc["ativo"] = False
        return True


class FakeDisciplinaDao:
    def __init__(self):
        self.documentos = {}

    def campo_existe(self, campo, valor):
        return any(doc.get(campo) == valor for doc in self.documentos.values())

    def criar(self, disciplina):
        self.documentos[disciplina.codigo_disciplina] = self._doc(disciplina)
        return True

    def consulta(self, filtro=None):
        return [deepcopy(doc) for doc in self.documentos.values()]

    def atualizar(self, disciplina):
        if disciplina.codigo_disciplina not in self.documentos:
            return False
        self.documentos[disciplina.codigo_disciplina] = self._doc(disciplina)
        return True

    def excluir(self, codigo):
        doc = self.documentos.get(codigo)
        if not doc or not doc["ativo"]:
            return False
        doc["ativo"] = False
        return True

    @staticmethod
    def _doc(disciplina):
        return {
            "codigo_disciplina": disciplina.codigo_disciplina,
            "nome_disciplina": disciplina.nome_disciplina,
            "professor": {"registro": disciplina.professor.registro, "nome": disciplina.professor.nome},
            "turma": disciplina.turma,
            "alunos": list(disciplina.alunos),
            "ativo": True,
        }


class FakeQuestaoDao:
    def __init__(self):
        self.documentos = {}
        self.sequencia = 0

    def campo_existe(self, campo, valor):
        return any(str(doc.get(campo, "")).lower() == str(valor).lower() for doc in self.documentos.values())

    def criar(self, questao):
        self.sequencia += 1
        id_questao = f"{self.sequencia:024x}"
        doc = self._doc(questao)
        doc["_id"] = id_questao
        self.documentos[id_questao] = doc
        return id_questao

    def consulta(self, filtro=None):
        resultado = []
        for doc in self.documentos.values():
            if doc.get("ativo") is False:
                continue
            seguro = deepcopy(doc)
            seguro.pop("ativo", None)
            resultado.append(seguro)
        return resultado

    def buscar_por_ids(self, ids_questoes):
        return [
            deepcopy(self.documentos[id_questao])
            for id_questao in ids_questoes
            if id_questao in self.documentos
            and self.documentos[id_questao].get("ativo") is not False
        ]

    def atualizar(self, questao):
        if questao.id_hash not in self.documentos:
            return False
        doc = self._doc(questao)
        doc["_id"] = questao.id_hash
        self.documentos[questao.id_hash] = doc
        return True

    def excluir(self, id_questao):
        doc = self.documentos.get(id_questao)
        if not doc or not doc["ativo"]:
            return False
        doc["ativo"] = False
        return True

    @staticmethod
    def _doc(questao):
        doc = {
            "professor": {"nome": questao.professor.nome},
            "assunto": questao.assunto,
            "disciplina": list(questao.disciplina),
            "tipo_questao": questao.tipo_questao,
            "dificuldade": questao.dificuldade,
            "autor": questao.autor,
            "enunciado": questao.enunciado,
            "ativo": True,
        }
        if questao.tipo_questao == "Objetiva":
            doc["alternativas"] = [
                {"id": alternativa.id, "texto": alternativa.texto}
                for alternativa in questao.alternativas
            ]
            doc["alternativa_correta"] = questao.alternativa_correta
        else:
            doc["numero_linhas"] = questao.numero_linhas
        return doc


class FakeProvaDao:
    def __init__(self):
        self.documentos = {}
        self.sequencia = 0

    def criar(self, prova):
        self.sequencia += 1
        id_prova = f"{1000 + self.sequencia:024x}"
        self.documentos[id_prova] = self._doc(prova, id_prova)
        return id_prova

    def consulta(self, filtro=None):
        resultado = []
        for doc in self.documentos.values():
            if not doc["ativo"]:
                continue
            seguro = deepcopy(doc)
            seguro.pop("ativo", None)
            resultado.append(seguro)
        return resultado

    def campo_existe(self, campo, valor):
        return valor in self.documentos and self.documentos[valor]["ativo"]

    def atualizar(self, prova):
        if prova.id_hash not in self.documentos:
            return False
        self.documentos[prova.id_hash] = self._doc(prova, prova.id_hash)
        return True

    def excluir(self, id_prova):
        doc = self.documentos.get(id_prova)
        if not doc or not doc["ativo"]:
            return False
        doc["ativo"] = False
        return True

    @staticmethod
    def _doc(prova, id_prova):
        return {
            "_id": id_prova,
            "id_turma": deepcopy(prova.id_turma),
            "professor": {"nome": prova.professor.nome},
            "disciplina": {"codigo_disciplina": prova.disciplina.codigo_disciplina, "nome_disciplina": prova.disciplina.nome_disciplina},
            "status": prova.status,
            "tipo": prova.tipo,
            "serie": prova.serie,
            "bimestre": prova.bimestre,
            "data_de_aplicacao": prova.data_de_aplicacao,
            "questoes": deepcopy(prova.questoes),
            "ativo": True,
        }
