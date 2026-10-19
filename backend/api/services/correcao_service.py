import logging
from bson import ObjectId
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from threading import BoundedSemaphore
from datetime import datetime, timezone
from uuid import uuid4
from math import isfinite

from api.modelos.prova import Prova
from api.utils.resposta_erro_http import resposta_erro_http


class Correcao_service:
    def __init__(self, cliente, prova_x_aluno_dao, aluno_dao, prova_dao, concorrencia=8, lote_dao=None):
        if concorrencia < 1:
            raise ValueError("A concorrência deve ser maior que zero")
        self.cliente = cliente
        self.prova_x_aluno_dao = prova_x_aluno_dao
        self.aluno_dao = aluno_dao
        self.prova_dao = prova_dao
        self.lote_dao = lote_dao
        self.concorrencia = concorrencia
        # O executor é compartilhado por todas as requisições deste processo.
        self._executor = ThreadPoolExecutor(max_workers=concorrencia)
        self._vagas = BoundedSemaphore(concorrencia * 2)

    def corrigir(self, imagens):
        resultados = []
        erros = []
        pendentes = {}
        proximo = 0
        while proximo < len(imagens) or pendentes:
            while proximo < len(imagens) and len(pendentes) < self.concorrencia:
                indice = proximo
                imagem = imagens[indice]
                proximo += 1
                if not self._vagas.acquire(timeout=1):
                    erros.append(self._erro(indice, imagem, 503, "Fila de correção ocupada; tente novamente"))
                    continue
                try:
                    futuro = self._executor.submit(self._corrigir_imagem, imagem)
                except Exception:
                    self._vagas.release()
                    raise
                futuro.add_done_callback(lambda _: self._vagas.release())
                pendentes[futuro] = (indice, imagem)

            if not pendentes:
                continue
            concluidos, _ = wait(pendentes, return_when=FIRST_COMPLETED)
            for futuro in concluidos:
                indice, imagem = pendentes.pop(futuro)
                try:
                    resultado = futuro.result()
                    resultados.append({"indice": indice, "arquivo": imagem["arquivo"], **resultado})
                except resposta_erro_http as erro:
                    erros.append(self._erro(indice, imagem, erro.httpCode, erro.mensagem, registrar_tentativa=erro.httpCode != 409))
                except Exception:
                    logging.exception("Falha ao corrigir arquivo do lote")
                    erros.append(self._erro(indice, imagem, 500, "Falha interna na correção", registrar_tentativa=True))

        return {
            "resultados": sorted(resultados, key=lambda item: item["indice"]),
            "erros": sorted(erros, key=lambda item: item["indice"])
        }

    def _corrigir_imagem(self, imagem):
        imagem.pop("_registro_correcao", None)
        dados = self.cliente.processar(imagem)
        id_prova_aluno = dados.get("qrcode")
        if not isinstance(id_prova_aluno, str) or not id_prova_aluno.strip() or id_prova_aluno.strip() == "NÃO ENCONTRADO":
            raise resposta_erro_http(422, "QR Code não encontrado ou inválido")
        # O QR do leitor prevalece. O ID enviado pelo navegador só identifica falhas.
        imagem["id_prova_aluno"] = id_prova_aluno.strip()
        registro = self.prova_x_aluno_dao.buscar_por_id(id_prova_aluno.strip())
        if not registro:
            raise resposta_erro_http(404, "ProvaXAluno não encontrada")
        # A falha só pode ser associada à mesma versão que foi efetivamente lida.
        imagem["_registro_correcao"] = registro

        id_prova = registro.get("id_prova")
        prova = self.prova_dao.buscar_por_id(id_prova.strip()) if isinstance(id_prova, str) and id_prova.strip() else None
        if not prova:
            raise resposta_erro_http(404, "Prova-base não encontrada ou inativa")

        questoes = registro.get("questoes", [])
        if not 1 <= len(questoes) <= Prova.MAX_QUESTOES:
            raise resposta_erro_http(422, f"O leitor suporta provas de 1 a {Prova.MAX_QUESTOES} questões")
        quantidade = prova.get("quantidade_questoes")
        if quantidade is not None and (len(questoes) != quantidade or len(prova.get("questoes", [])) != quantidade):
            raise resposta_erro_http(422, "Quantidade de questões incompatível com a prova-base")
        aluno = self.aluno_dao.buscar_por_matricula(registro["matricula_aluno"])
        if not aluno:
            raise resposta_erro_http(404, "Aluno não encontrado")

        respostas = dados.get("respostas")
        if not isinstance(respostas, dict):
            raise resposta_erro_http(502, "Respostas inválidas do microserviço")

        gabarito_aluno = {}
        gabarito_correto = {}
        for numero, questao in enumerate(questoes, start=1):
            chave = str(numero)
            if chave not in respostas:
                raise resposta_erro_http(502, "O microserviço omitiu uma resposta esperada")
            resposta = respostas[chave]
            if resposta is not None and resposta not in ("A", "B", "C", "D", "E"):
                raise resposta_erro_http(502, "Alternativa inválida retornada pelo microserviço")
            posicao = questao.get("posicao_alternativa_correta")
            if type(posicao) is not int or not 1 <= posicao <= 5:
                raise resposta_erro_http(422, "Gabarito individual com posição inválida")
            gabarito_aluno[chave] = resposta
            gabarito_correto[chave] = "ABCDE"[posicao - 1]

        acertos = sum(gabarito_aluno[chave] == correta for chave, correta in gabarito_correto.items())
        resultado = {
            "id_correcao": uuid4().hex,
            "corrigida_em": datetime.now(timezone.utc).isoformat(),
            "id_prova_aluno": registro["_id"],
            "id_prova": registro["id_prova"],
            "matricula": registro["matricula_aluno"],
            "nome": aluno["nome_aluno"],
            "turma": aluno.get("turma", ""),
            "nota_prova": round(acertos / len(questoes) * 10, 2),
            "gabarito_aluno": gabarito_aluno,
            "gabarito_correto": gabarito_correto
        }
        if not self.prova_x_aluno_dao.salvar_correcao(registro, resultado):
            raise resposta_erro_http(409, "A versão individual mudou durante a correção. Envie a imagem novamente")
        self._atualizar_status_correcao(id_prova.strip(), prova)
        return resultado

    def _atualizar_status_correcao(self, id_prova, prova):
        if prova.get("status") != Prova.STATUS_IMPRESSA:
            return
        contagem = self.prova_x_aluno_dao.contar_correcoes(id_prova)
        if contagem["total"] > 0 and contagem["processadas"] == contagem["total"]:
            # A contagem considera todas as versões da base, não só o envio atual.
            self.prova_dao.marcar_corrigida(id_prova)

    def criar_lote(self, entradas):
        if not isinstance(entradas, list) or not entradas:
            raise resposta_erro_http(400, "Informe as entradas do lote na ordem das imagens enviadas")
        ids = []
        for entrada in entradas:
            if not isinstance(entrada, dict) or not isinstance(entrada.get("arquivo"), str):
                raise resposta_erro_http(400, "Entrada de lote inválida")
            if entrada.get("erro") is True:
                if set(entrada) - {"arquivo", "erro"}:
                    raise resposta_erro_http(400, "Entrada com falha inválida")
                continue
            if set(entrada) != {"arquivo", "id_prova_aluno", "id_correcao"} or not isinstance(entrada["id_prova_aluno"], str) or not ObjectId.is_valid(entrada["id_prova_aluno"]) or not isinstance(entrada["id_correcao"], str):
                raise resposta_erro_http(400, "Informe apenas os identificadores da correção, sem notas enviadas pelo frontend")
            ids.append(entrada["id_prova_aluno"])
        if len(ids) != len(set(ids)):
            raise resposta_erro_http(400, "Há cartões repetidos no lote. Selecione uma imagem por folha")
        registros = {item["_id"]: item for item in self.prova_x_aluno_dao.buscar_por_ids(ids)} if ids else {}
        itens = []
        for indice, entrada in enumerate(entradas):
            item = {"posicao": indice + 1, "arquivo": entrada["arquivo"], "corrigida": entrada.get("erro") is not True}
            if item["corrigida"]:
                correcao = registros.get(entrada["id_prova_aluno"], {}).get("correcao")
                if not correcao or correcao.get("id_correcao") != entrada["id_correcao"]:
                    raise resposta_erro_http(409, "Uma correção não está mais disponível. Corrija o conjunto novamente antes de imprimir")
                if not all(isinstance(correcao.get(campo), str) and correcao[campo].strip() for campo in ("nome", "turma")):
                    raise resposta_erro_http(409, "Confira o nome e a turma dos alunos antes de imprimir notas")
                nota = correcao.get("nota_prova")
                if type(nota) not in (int, float) or not isfinite(nota) or not 0 <= nota <= 10:
                    raise resposta_erro_http(409, "Uma nota salva é inválida para impressão. Corrija o conjunto novamente")
                item.update({campo: correcao[campo] for campo in ("id_correcao", "id_prova_aluno", "id_prova", "matricula", "nome", "turma", "nota_prova")})
            itens.append(item)
        # Cópia imutável das notas e da ordem deste envio, não uma consulta à última nota.
        return self.lote_dao.criar({"criado_em": datetime.now(timezone.utc).isoformat(), "itens": itens,
                                   "imprimivel": all(item["corrigida"] for item in itens)})

    def buscar_lote(self, id_lote):
        lote = self.lote_dao.buscar_por_id(id_lote)
        if not lote:
            raise resposta_erro_http(404, "Lote de correção não encontrado")
        return lote

    def _erro(self, indice, imagem, codigo, mensagem, registrar_tentativa=False):
        erro = {"indice": indice, "arquivo": imagem["arquivo"], "codigo": codigo, "mensagem": mensagem,
                "matricula": None, "nome": None, "turma": None}
        id_ = imagem.get("id_prova_aluno")
        if not isinstance(id_, str) or not ObjectId.is_valid(id_):
            return erro
        registro = None
        try:
            registro = imagem.get("_registro_correcao") or self.prova_x_aluno_dao.buscar_por_id(id_)
            if registro:
                erro["matricula"] = registro.get("matricula_aluno")
                aluno = self.aluno_dao.buscar_por_matricula(erro["matricula"])
                if aluno:
                    erro.update(nome=aluno.get("nome_aluno"), turma=aluno.get("turma"))
        except Exception:
            # A consulta de identificação não pode interromper as outras correções.
            logging.exception("Falha ao identificar aluno de uma correção pendente")
        if registrar_tentativa and registro:
            try:
                id_prova = registro.get("id_prova")
                prova = self.prova_dao.buscar_por_id(id_prova) if isinstance(id_prova, str) and id_prova.strip() else None
                if prova and self.prova_x_aluno_dao.registrar_tentativa_correcao(registro, {
                    "concluida_em": datetime.now(timezone.utc).isoformat(), "sucesso": False
                }):
                    self._atualizar_status_correcao(id_prova, prova)
            except Exception:
                # Uma falha de persistência não pode contar como uma tentativa registrada.
                logging.exception("Falha ao registrar tentativa de correção")
        return erro

    def fechar(self):
        self._executor.shutdown(wait=True)
        self.cliente.fechar()
