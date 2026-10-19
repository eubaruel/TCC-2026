from copy import deepcopy
from threading import Lock
from api.modelos.prova import Prova


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
            if all(doc.get(chave) in valor["$in"] if isinstance(valor, dict) and "$in" in valor
                   else doc.get(chave) == valor for chave, valor in filtro.items()):
                seguro = deepcopy(doc)
                seguro.pop("email_aluno", None)
                resultado.append(seguro)
        return resultado

    def buscar_matriculas_por_turmas(self, turmas):
        return [
            doc["matricula_aluno"]
            for doc in self.documentos.values()
            if doc.get("turma") in turmas and doc.get("ativo") is not False
        ]

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
        self.provas = {}

    def usada_em_prova_concluida(self, id_questao):
        return any(id_questao in prova.get("questoes", []) and prova.get("ativo") is not False
                   and prova.get("status") not in Prova.STATUS_EDITAVEIS for prova in self.provas.values())

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
        doc["alternativas"] = [
            {"id": alternativa.id, "texto": alternativa.texto}
            for alternativa in questao.alternativas
        ]
        doc["alternativa_correta"] = questao.alternativa_correta
        return doc


class FakeProvaDao:
    def __init__(self):
        self.documentos = {}
        self.sequencia = 0
        self._reserva_lock = Lock()

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
            corresponde = True
            for campo, esperado in (filtro or {}).items():
                valor = doc
                for parte in campo.split("."):
                    valor = valor.get(parte) if isinstance(valor, dict) else None
                if valor != esperado and not (isinstance(valor, list) and esperado in valor):
                    corresponde = False
                    break
            if not corresponde:
                continue
            seguro = deepcopy(doc)
            seguro.pop("ativo", None)
            seguro.pop("operacao_em_andamento", None)
            seguro.pop("geracao_pendente", None)
            resultado.append(seguro)
        return resultado

    def buscar_por_id(self, id_prova):
        doc = self.documentos.get(id_prova)
        if not doc or not doc["ativo"]:
            return None
        seguro = deepcopy(doc)
        seguro.pop("ativo", None)
        seguro.pop("operacao_em_andamento", None)
        return seguro

    def reservar_operacao(self, id_prova, token):
        with self._reserva_lock:
            doc = self.documentos.get(id_prova)
            if not doc or not doc["ativo"] or "operacao_em_andamento" in doc:
                return False
            doc["operacao_em_andamento"] = token
            return True

    def liberar_operacao(self, id_prova, token):
        with self._reserva_lock:
            doc = self.documentos.get(id_prova)
            if doc and doc.get("operacao_em_andamento") == token:
                doc.pop("operacao_em_andamento")

    def concluir_geracao(self, id_prova, token):
        doc = self.documentos.get(id_prova)
        if not self._pode_alterar(doc, token):
            return False
        doc.pop("geracao_pendente", None)
        return True

    @staticmethod
    def _pode_alterar(doc, token):
        return bool(doc and doc["ativo"] and doc["status"] in Prova.STATUS_EDITAVEIS
                    and doc.get("operacao_em_andamento") == token)

    def atualizar_questoes(self, id_prova, ids_questoes, token=None, geracao_pendente=False):
        doc = self.documentos.get(id_prova)
        if not self._pode_alterar(doc, token):
            return False
        doc["questoes"] = deepcopy(ids_questoes)
        doc["status"] = "Em elaboração"
        if geracao_pendente:
            doc["geracao_pendente"] = True
        return True

    def enviar(self, id_prova, ids_questoes, token=None):
        doc = self.documentos.get(id_prova)
        if not self._pode_alterar(doc, token) or doc["questoes"] != ids_questoes or doc.get("geracao_pendente"):
            return False
        doc["status"] = Prova.STATUS_ENVIADA
        return True

    def campo_existe(self, campo, valor):
        return valor in self.documentos and self.documentos[valor]["ativo"]

    def confirmar_impressao(self, id_prova, token):
        doc = self.documentos.get(id_prova)
        if not doc or not doc["ativo"] or doc["status"] != Prova.STATUS_ENVIADA or doc.get("operacao_em_andamento") != token or doc.get("geracao_pendente"):
            return False
        doc["status"] = Prova.STATUS_IMPRESSA
        return True

    def marcar_corrigida(self, id_prova):
        doc = self.documentos.get(id_prova)
        if not doc or not doc["ativo"] or doc["status"] != Prova.STATUS_IMPRESSA:
            return False
        doc["status"] = Prova.STATUS_CORRIGIDA
        return True

    def atualizar(self, prova, token=None):
        doc = self.documentos.get(prova.id_hash)
        if not self._pode_alterar(doc, token):
            return False
        doc.update(self._doc(prova, prova.id_hash))
        return True

    def excluir(self, id_prova, token=None):
        doc = self.documentos.get(id_prova)
        if not self._pode_alterar(doc, token):
            return False
        doc["ativo"] = False
        return True

    @staticmethod
    def _doc(prova, id_prova):
        professor = {"nome": prova.professor.nome}
        if prova.professor.registro is not None:
            professor["registro"] = prova.professor.registro

        return {
            "_id": id_prova,
            "id_turma": deepcopy(prova.id_turma),
            "professor": professor,
            "disciplina": {"codigo_disciplina": prova.disciplina.codigo_disciplina, "nome_disciplina": prova.disciplina.nome_disciplina},
            "status": prova.status,
            "tipo": prova.tipo,
            "serie": prova.serie,
            "periodo_letivo": prova.periodo_letivo,
            "data_de_aplicacao": prova.data_de_aplicacao,
            "quantidade_questoes": prova.quantidade_questoes,
            "questoes": deepcopy(prova.questoes),
            "ativo": True,
        }


class FakeProvaXAlunoDao:
    def __init__(self):
        self.documentos = {}

    def contar_correcoes(self, id_prova):
        versoes = [doc for doc in self.documentos.values() if doc["id_prova"] == id_prova]
        return {"total": len(versoes), "processadas": sum(
            doc.get("tentativa_correcao") is not None or doc.get("correcao", {}).get("id_correcao") is not None
            for doc in versoes
        )}

    def sincronizar(self, id_prova, provas_x_alunos):
        matriculas_atuais = {
            prova_x_aluno.matricula_aluno
            for prova_x_aluno in provas_x_alunos
        }
        self.documentos = {
            chave: documento
            for chave, documento in self.documentos.items()
            if chave[0] != id_prova or chave[1] in matriculas_atuais
        }

        for prova_x_aluno in provas_x_alunos:
            documento = {
                "_id": self.documentos.get(
                    (id_prova, prova_x_aluno.matricula_aluno), {}
                ).get("_id", f"{len(self.documentos) + 1:024x}"),
                "matricula_aluno": prova_x_aluno.matricula_aluno,
                "id_prova": prova_x_aluno.id_prova,
                "questoes": deepcopy(prova_x_aluno.questoes)
            }
            chave = (documento["id_prova"], documento["matricula_aluno"])
            self.documentos[chave] = documento

        return len(provas_x_alunos)

    def buscar_por_id_prova(self, id_prova):
        documentos = [
            deepcopy(documento)
            for (id_documento, _), documento in self.documentos.items()
            if id_documento == id_prova
        ]
        return sorted(
            documentos,
            key=lambda documento: documento["matricula_aluno"]
        )
