import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from professor import Professor

print("TESTANDO PROFESSOR")

prof = Professor()

# Nome válido
try:
    prof.nome_professor = "João Silva"
    print("OK - nome válido")
except Exception as e:
    print("ERRO - nome válido:", e)

# Nome inválido
try:
    prof.nome_professor = "Jo"
    print("ERRO - nome inválido passou")
except:
    print("OK - nome inválido")

# Email válido
try:
    prof.email_professor = "teste@email.com"
    print("OK - email válido")
except Exception as e:
    print("ERRO - email válido:", e)

# Email inválido
try:
    prof.email_professor = "email"
    print("ERRO - email inválido passou")
except:
    print("OK - email inválido")