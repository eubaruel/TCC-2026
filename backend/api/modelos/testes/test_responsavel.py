import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from responsavel import Responsavel
from aluno import Aluno

print("TESTANDO RESPONSAVEL")

resp = Responsavel()
aluno = Aluno()

aluno.nome_aluno = "Pedro Silva"

# Nome válido
try:
    resp.nome_responsavel = "Maria Oliveira"
    print("OK - nome válido")
except Exception as e:
    print("ERRO:", e)

# Nome inválido
try:
    resp.nome_responsavel = "Ana"
    print("ERRO - nome inválido passou")
except:
    print("OK - nome inválido")

# Telefone válido
try:
    resp.telefone_responsavel = "(12) 99999-9999"
    print("OK - telefone válido")
except Exception as e:
    print("ERRO:", e)

# Aluno válido
try:
    resp.aluno = aluno
    print("OK - aluno válido")
except Exception as e:
    print("ERRO:", e)