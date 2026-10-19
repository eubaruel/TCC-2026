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
