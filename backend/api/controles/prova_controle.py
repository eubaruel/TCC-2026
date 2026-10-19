import json
from bson import ObjectId
from flask import request,jsonify
from api.services.prova_service import Prova_service
from api.utils.resposta_json import Resposta_json
from api.utils.resposta_erro_http import resposta_erro_http

class Prova_controle:
    def __init__(self, prova_service:Prova_service, correcao_service=None):
        print("⬆️  Prova_controle.constructor()")
        self.__prova_service = prova_service
        self.__correcao_service = correcao_service

    def corrigir_provas(self):
        arquivos = request.files.getlist("imagens")
        if not arquivos or len(arquivos) > 50:
            raise resposta_erro_http(400, "Envie de 1 a 50 arquivos no campo 'imagens'")
        try:
            ids = json.loads(request.form["ids_provas_alunos"]) if "ids_provas_alunos" in request.form else [None] * len(arquivos)
        except ValueError:
            raise resposta_erro_http(400, "ids_provas_alunos deve ser uma lista JSON")
        if not isinstance(ids, list) or len(ids) != len(arquivos) or any(
            id_ is not None and (not isinstance(id_, str) or not ObjectId.is_valid(id_)) for id_ in ids
        ):
            raise resposta_erro_http(400, "Informe um identificador válido ou null para cada imagem")
        imagens = []
        for arquivo, id_prova_aluno in zip(arquivos, ids):
            conteudo = arquivo.read(5 * 1024 * 1024 + 1)
            if not conteudo:
                raise resposta_erro_http(400, "Uma das imagens está vazia")
            if len(conteudo) > 5 * 1024 * 1024:
                raise resposta_erro_http(413, "Cada imagem deve ter no máximo 5 MiB")
            imagens.append({
                "arquivo": arquivo.filename or "cartao-resposta",
                "bytes": conteudo,
                "content_type": arquivo.mimetype or "application/octet-stream",
                "id_prova_aluno": id_prova_aluno
            })
        resultado = self.__correcao_service.corrigir(imagens)
        return Resposta_json.sucesso(
            mensagem="Correções processadas", data=resultado, codigo=200
        )

    def criar_prova(self):
        print("🔵 prova_controle.criar_prova()")
        json_prova = request.json.get("prova")
        prova_criada = self.__prova_service.criar_prova(json_prova)

        return Resposta_json.sucesso(
            mensagem = "Prova criada com sucesso",
            data = {"prova": prova_criada},
            codigo = 201
        )

    def criar_lote_correcao(self):
        corpo = request.get_json(silent=True)
        if not isinstance(corpo, dict) or set(corpo) != {"entradas"}:
            raise resposta_erro_http(400, "Informe somente o campo entradas")
        return Resposta_json.sucesso(mensagem="Lote de correção salvo",
            data={"lote": self.__correcao_service.criar_lote(corpo["entradas"])}, codigo=201)

    def buscar_lote_correcao(self, _id):
        return Resposta_json.sucesso(mensagem="Lote de correção encontrado",
            data={"lote": self.__correcao_service.buscar_lote(_id)}, codigo=200)

    def adicionar_questoes(self, _id):
        print("🔵 prova_controle.adicionar_questoes()")

        json_prova = request.json.get("prova")
        resultado = self.__prova_service.adicionar_questoes(
            _id,
            json_prova.get("questoes")
        )

        return Resposta_json.sucesso(
            mensagem = "Questões adicionadas com sucesso",
            data = resultado,
            codigo = 200
        )

    def imprimir_provas(self, _id):
        print("🔵 prova_controle.imprimir_provas()")

        provas_alunos = self.__prova_service.imprimir_provas(_id)
        return Resposta_json.sucesso(
            mensagem = "Provas montadas com sucesso",
            data = {
                "id_prova": _id,
                "provas_alunos": provas_alunos
            },
            codigo = 200
        )

    def enviar(self, _id):
        return Resposta_json.sucesso(
            mensagem="Prova enviada ao processo pedagógico",
            data=self.__prova_service.enviar(_id), codigo=200
        )
    
    
    def confirmar_impressao(self, _id):
        return Resposta_json.sucesso(
            mensagem="Impressão confirmada",
            data=self.__prova_service.confirmar_impressao(_id), codigo=200
        )

    def ignorar_provas_nao_corrigidas(self, _id):
        return Resposta_json.sucesso(
            mensagem="Prova marcada como corrigida; versões restantes ignoradas",
            data=self.__prova_service.ignorar_provas_nao_corrigidas(_id), codigo=200
        )

    def ler(self):
        print("🔵 prova_controle.ler()")

        tipos = {
            "serie":int,
            "registro":int,
        }

        campos_permitidos = ["id","id_turma","codigo_disciplina",
                            "nome_disciplina","nome","registro",
                            "status","tipo","serie","periodo_letivo",
                            "data_de_aplicacao"
                            ]
        
        filtro, erro = self._formatar_pesquisa(
            tipos = tipos,
            campos_permitidos = campos_permitidos,
            args = request.args.items()
        )

        if erro:
            return Resposta_json.erro(mensagem = erro, codigo = 400)
        
        consulta = self.__prova_service.consulta(filtro)

        return Resposta_json.sucesso(
            mensagem = "Executado com sucesso",
            data = {"provas":consulta},
            codigo = 200
        )
    
    
    def alterar(self,_id):
        print("🔵 prova_controle.alterar()")

        json_prova = request.json.get("prova")
        sucesso = self.__prova_service.atualizar(json_prova, _id)
        if sucesso:
            return Resposta_json.sucesso(
                mensagem = "Atualizado com sucesso",
                data = {"prova":self._formatar_prova(json_prova, _id)},
                codigo = 200
            )
        else:
            return Resposta_json.erro(
                mensagem = "Não foi possível atualizar a prova",
                codigo = 400
            )
        
    
    def deletar(self, _id):
        print("🔵 prova_controle.deletar()")

        excluiu = self.__prova_service.excluir(_id)
        if excluiu:
            return Resposta_json.sucesso(
                mensagem = "Excluído com sucesso",
                data = None,
                codigo = 200
            )
        else:
            return Resposta_json.erro(
                mensagem = f"Não existe prova com o id {_id}",
                codigo = 404
            )
        
    def _formatar_pesquisa(self,tipos,campos_permitidos,args):
        filtro = {}

        for key, value in args:
            if not value:
                continue

            if key not in campos_permitidos:
                return None, f"Parâmetro não permitido: {key}"

            conversor = tipos.get(key,str)

            try:
                if key == "id":
                    filtro["_id"] = value

                elif key == "nome":
                    filtro["professor.nome"] = conversor(value)

                elif key == "registro":
                    filtro["professor.registro"] = conversor(value)

                elif key == "codigo_disciplina":
                    filtro["disciplina.codigo_disciplina"] = conversor(value)

                elif key == "nome_disciplina":
                    filtro["disciplina.nome_disciplina"] = conversor(value)

                else:
                    filtro[key] = conversor(value)
            except ValueError:
                return None, f"{key} inválido: {value}"
            
        return filtro, None
    
    def _formatar_prova(self,prova, id_hash):
        professor = prova.get("professor")
        disciplina = prova.get("disciplina")

        formatado = {
            "_id":id_hash,
            "id_turma":prova.get("id_turma"),
            "professor":{
                "nome":professor.get("nome"),
                "registro":professor.get("registro")
            },
            "disciplina":{
                "codigo_disciplina":disciplina.get("codigo_disciplina"),
                "nome_disciplina":disciplina.get("nome_disciplina")
            },
            "status":prova.get("status"),
            "tipo":prova.get("tipo"),
            "serie":prova.get("serie"),
            "periodo_letivo":prova.get("periodo_letivo"),
            "data_de_aplicacao":prova.get("data_de_aplicacao"),
            "questoes":prova.get("questoes"),
            "quantidade_questoes": prova.get("quantidade_questoes")
        }

        return formatado
