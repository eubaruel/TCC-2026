import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aluno import Aluno

print("\n===== TESTES ALUNO =====")

# TESTE 1 - válido
try:
    aluno = Aluno()
    aluno.id_hash = "abc123"
    aluno.matricula_aluno = 12345678
    aluno.nome_aluno = "Joao Silva"
    aluno.turma = "Turma 2024 A"
    aluno.serie = 3
    aluno.situacao = "Ativo"
    aluno.email_aluno = "joao@email.com"
    print("✔ Teste válido passou")
except Exception as e:
    print("✘ Teste válido falhou:", e)

# TESTE 2 - matrícula inválida
try:
    aluno = Aluno()
    aluno.matricula_aluno = 123
    print("✘ Falhou: matrícula inválida aceita")
except:
    print("✔ Matrícula inválida bloqueada")

# TESTE 3 - nome inválido
try:
    aluno = Aluno()
    aluno.nome_aluno = "Ana"
    print("✘ Falhou: nome inválido aceito")
except:
    print("✔ Nome inválido bloqueado")

# TESTE 4 - email inválido
try:
    aluno = Aluno()
    aluno.email_aluno = "email_errado"
    print("✘ Falhou: email inválido aceito")
except:
    print("✔ Email inválido bloqueado")

# TESTE 5 - situação com número
try:
    aluno = Aluno()
    aluno.situacao = "Ativo123"
    print("✘ Falhou: situação inválida aceita")
except:
    print("✔ Situação inválida bloqueada")