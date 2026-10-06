import logging
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from threading import BoundedSemaphore

from api.utils.resposta_erro_http import resposta_erro_http


class Correcao_service:
    def __init__(self, cliente, prova_x_aluno_dao, aluno_dao, concorrencia=8):
        if concorrencia < 1:
            raise ValueError("A concorrência deve ser maior que zero")
        self.cliente = cliente
        self.prova_x_aluno_dao = prova_x_aluno_dao
        self.aluno_dao = aluno_dao
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
                    erros.append(self._erro(indice, imagem, erro.httpCode, erro.mensagem))
                except Exception:
                    logging.exception("Falha ao corrigir arquivo do lote")
                    erros.append(self._erro(indice, imagem, 500, "Falha interna na correção"))

        return {
            "resultados": sorted(resultados, key=lambda item: item["indice"]),
            "erros": sorted(erros, key=lambda item: item["indice"])
        }

    def _corrigir_imagem(self, imagem):
        dados = self.cliente.processar(imagem)
        id_prova_aluno = dados.get("qrcode")
        if not isinstance(id_prova_aluno, str) or not id_prova_aluno.strip() or id_prova_aluno.strip() == "NÃO ENCONTRADO":
            raise resposta_erro_http(422, "QR Code não encontrado ou inválido")
        registro = self.prova_x_aluno_dao.buscar_por_id(id_prova_aluno.strip())
        if not registro:
            raise resposta_erro_http(404, "ProvaXAluno não encontrada")

        questoes = registro.get("questoes", [])
        if not 1 <= len(questoes) <= 10:
            raise resposta_erro_http(422, "O leitor suporta provas de 1 a 10 questões")
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
        return {
            "id_prova_aluno": registro["_id"],
            "matricula": registro["matricula_aluno"],
            "nome": aluno["nome_aluno"],
            "nota_prova": round(acertos / len(questoes) * 10, 2),
            "gabarito_aluno": gabarito_aluno,
            "gabarito_correto": gabarito_correto
        }

    @staticmethod
    def _erro(indice, imagem, codigo, mensagem):
        return {"indice": indice, "arquivo": imagem["arquivo"], "codigo": codigo, "mensagem": mensagem}

    def fechar(self):
        self._executor.shutdown(wait=True)
        self.cliente.fechar()
