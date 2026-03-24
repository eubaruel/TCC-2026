import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from questao import Questao
from professor import Professor

print("TESTANDO QUESTAO")

q = Questao()
prof = Professor()

prof.nome_professor = "João Silva"

# Tipo
try:
    q.tipo_questao = "objetiva"
    print("OK - tipo questão")
except Exception as e:
    print("ERRO:", e)

# Alternativas válidas
try:
    q.alternativas = ["A", "B", "C", "D", "E"]
    print("OK - alternativas")
except Exception as e:
    print("ERRO:", e)

# Alternativa correta
try:
    q.alternativa_correta = "A"
    print("OK - alternativa correta")
except Exception as e:
    print("ERRO:", e)

# Alternativa inválida
try:
    q.alternativa_correta = "X"
    print("ERRO - alternativa inválida passou")
except:
    print("OK - alternativa inválida")