from threading import local, Lock

import requests

from api.utils.resposta_erro_http import resposta_erro_http


class Correcao_cliente:
    """Uma sessão por worker permite reutilizar conexões sem compartilhar sessões."""

    def __init__(self, url, timeout=30):
        if timeout <= 0:
            raise ValueError("O timeout de correção deve ser positivo")
        self.url = url.rstrip("/") + "/processar"
        self.timeout = timeout
        self._local = local()
        self._sessoes = []
        self._lock = Lock()

    def processar(self, imagem):
        if not hasattr(self._local, "sessao"):
            sessao = requests.Session()
            self._local.sessao = sessao
            with self._lock:
                self._sessoes.append(sessao)
        try:
            with self._local.sessao.post(
                self.url,
                files={"imagem": (
                    imagem["arquivo"], imagem["bytes"], imagem["content_type"]
                )},
                timeout=(5, self.timeout)
            ) as resposta:
                resposta.raise_for_status()
                dados = resposta.json()
        except requests.Timeout as erro:
            raise resposta_erro_http(504, "Tempo limite do microserviço excedido") from erro
        except requests.RequestException as erro:
            raise resposta_erro_http(502, "Falha na comunicação com o microserviço") from erro
        except ValueError as erro:
            raise resposta_erro_http(502, "O microserviço retornou JSON inválido") from erro

        if not isinstance(dados, dict):
            raise resposta_erro_http(502, "Resposta inválida do microserviço")
        return dados

    def fechar(self):
        for sessao in self._sessoes:
            sessao.close()
