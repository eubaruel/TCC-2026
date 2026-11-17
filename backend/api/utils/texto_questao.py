import re
from html.parser import HTMLParser


LIMITE_ENUNCIADO = 7000
LIMITE_ALTERNATIVA = 2000
LIMITE_IMAGENS = 3


class _ContadorConteudoHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.caracteres = 0
        self.imagens = 0
        self.ignorar = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.ignorar = True
        elif tag == "img" and not self.ignorar:
            self.imagens += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.ignorar = False

    def handle_data(self, data):
        if not self.ignorar:
            self.caracteres += len(data)


def _ler_conteudo(html):
    contador = _ContadorConteudoHTML()
    # O parser HTML do navegador normaliza quebras de linha desta mesma forma.
    contador.feed(html.replace("\r\n", "\n").replace("\r", "\n"))
    contador.close()
    return contador


def contar_caracteres(html):
    return _ler_conteudo(html).caracteres


def validar_conteudo_questao(html, limite, campo):
    conteudo = _ler_conteudo(html)
    if conteudo.caracteres > limite:
        raise ValueError(
            f"{campo} deve ter no máximo {limite} caracteres de texto, incluindo espaços e pontuação"
        )
    if conteudo.imagens > LIMITE_IMAGENS:
        raise ValueError(f"{campo} deve ter no máximo {LIMITE_IMAGENS} imagens")


# O Quill 2 grava cada espaço como &nbsp;, o que impede a quebra de linha.
# Mantém o &nbsp; apenas onde ele preserva espaços consecutivos; <pre> fica intacto.
_ESPACO_DURO = " "
_NBSP = re.compile("&nbsp;|&#160;|&#xa0;|" + _ESPACO_DURO, re.IGNORECASE)
_ESPACOS = re.compile("[ " + _ESPACO_DURO + "]+")
_TRECHO_PRE = re.compile(r"(<pre\b.*?</pre>)", re.IGNORECASE | re.DOTALL)


def _normalizar_trecho(html):
    html = _NBSP.sub(_ESPACO_DURO, html)
    return _ESPACOS.sub(
        lambda m: " " if len(m.group(0)) == 1 else " " + "&nbsp;" * (len(m.group(0)) - 1),
        html,
    )


def normalizar_espacos(html):
    if not isinstance(html, str):
        return html
    partes = _TRECHO_PRE.split(html)
    return "".join(parte if i % 2 else _normalizar_trecho(parte) for i, parte in enumerate(partes))


class _ExtratorTexto(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.partes = []

    def handle_data(self, data):
        self.partes.append(data)


def resumo_texto(html, limite=80):
    extrator = _ExtratorTexto()
    extrator.feed(html or "")
    texto = " ".join("".join(extrator.partes).split())
    return texto if len(texto) <= limite else texto[:limite].rstrip() + "…"
