"""Corrige questões salvas com &nbsp; no lugar dos espaços (Quill 2).

Uso, a partir da pasta backend:
    python scripts/normalizar_nbsp_questoes.py          # só mostra o que mudaria
    python scripts/normalizar_nbsp_questoes.py --aplicar
"""
import os
import sys

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.utils.texto_questao import normalizar_espacos, resumo_texto  # noqa: E402


def main():
    aplicar = "--aplicar" in sys.argv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
    colecao = MongoClient(os.environ["URI_BD"])[os.environ["NOME_BD"]]["questoes"]

    alteradas = conflitos = 0
    for questao in colecao.find({}, {"enunciado": 1, "alternativas": 1}):
        enunciado = normalizar_espacos(questao.get("enunciado"))
        alternativas = [
            {**alternativa, "texto": normalizar_espacos(alternativa.get("texto"))}
            for alternativa in questao.get("alternativas") or []
        ]
        if enunciado == questao.get("enunciado") and alternativas == (questao.get("alternativas") or []):
            continue
        alteradas += 1
        print(f"{questao['_id']}: {resumo_texto(enunciado)}")
        if not aplicar:
            continue
        try:
            colecao.update_one({"_id": questao["_id"]}, {"$set": {"enunciado": enunciado, "alternativas": alternativas}})
        except DuplicateKeyError:
            conflitos += 1
            print("  conflito: já existe outra questão com este enunciado; mantida sem alteração")

    acao = "corrigidas" if aplicar else "a corrigir (rode com --aplicar)"
    print(f"\n{alteradas - conflitos} questões {acao}; {conflitos} conflitos.")


if __name__ == "__main__":
    main()
