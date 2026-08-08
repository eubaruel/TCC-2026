# Relatório de correções lógicas da API

Data da verificação: 6 de agosto de 2026  
Escopo: `backend`, sem alterar ou analisar `sistema-correcao`.

## Objetivo

Corrigir erros de lógica, integridade de dados, contratos HTTP e exposição excessiva de dados encontrados na API. JWT, CORS, HTTPS e demais configurações de produção ficaram deliberadamente fora deste trabalho.

## Resumo das correções

### Alunos

- A matrícula recebida no cadastro agora é atribuída ao modelo e persistida pelo DAO.
- `ativo` deixou de ser obrigatório no cadastro; novos alunos são ativados internamente.
- Atualizações respeitam o valor de `ativo` recebido.
- A listagem não retorna `email_aluno`.
- O filtro `ativo=false` passou a ser convertido corretamente.
- Parâmetros de pesquisa desconhecidos agora geram erro, em vez de serem ignorados.
- A exclusão bem-sucedida retorna HTTP 200 com o contrato JSON padronizado.
- Situações formadas apenas por números ou contendo números são rejeitadas.

Arquivos principais:

- `api/modelos/aluno.py`
- `api/middlewares/aluno_middleware.py`
- `api/controles/aluno_controle.py`
- `api/services/aluno_service.py`
- `api/DAOs/aluno_dao.py`
- `api/utils/conversores.py`

### Importação de alunos

- A importação não executa mais `delete_many({})`.
- Os registros são inseridos ou atualizados por matrícula usando `bulk_write` e `upsert`.
- Todas as colunas são verificadas antes da persistência.
- Linhas nulas, inválidas ou com matrícula duplicada dentro da planilha invalidam a operação antes da escrita.
- O resultado informa quantos registros foram processados, criados e atualizados.
- A planilha-modelo foi corrigida para usar matrícula válida de oito dígitos.

Motivo: impedir perda integral da coleção e garantir que a planilha de exemplo seja compatível com as regras do próprio modelo.

### Usuários

- `ativo` deixou de ser obrigatório no cadastro e continua sendo definido internamente como `True`.
- O PUT não exige mais `registro` duplicado no body; o identificador da URL é a fonte de verdade.
- Atualizações passam a respeitar o valor de `ativo`.
- O filtro booleano foi corrigido.
- Parâmetros desconhecidos geram erro.
- A exclusão bem-sucedida retorna HTTP 200.
- A listagem continua removendo o campo `senha`.

Arquivos principais:

- `api/middlewares/usuario_middleware.py`
- `api/controles/usuario_controle.py`
- `api/services/usuario_service.py`

Observação: as alterações preexistentes em `usuario_controle.py` e `usuario_rotas.py` para o fluxo `PATCH /senha` foram preservadas. Esse fluxo ainda estava incompleto antes desta tarefa e não fez parte das correções implementadas.

### Disciplinas

- Filtros por `registro` e `nome` agora pesquisam `professor.registro` e `professor.nome` no MongoDB.
- A listagem não retorna a lista completa de matrículas; retorna `quantidade_alunos`.
- A exclusão passou de física para lógica por meio de `ativo=False`.
- Documentos antigos sem o campo `ativo` continuam sendo tratados como ativos.
- Parâmetros de filtro desconhecidos são rejeitados.
- A exclusão bem-sucedida retorna HTTP 200.

Arquivos principais:

- `api/controles/disciplina_controle.py`
- `api/services/disciplina_service.py`
- `api/DAOs/disciplina_dao.py`

### Questões

- A listagem retorna `alternativa_correta`, pois o banco de questões é acessado exclusivamente por professores durante a montagem da prova.
- O campo interno `ativo` também não é exposto.
- A exclusão passou a ser lógica.
- O filtro `nome` foi mapeado para `professor.nome`.
- Questões inativas são omitidas das consultas.
- O middleware agora cruza `tipo_questao` com os campos específicos:
  - objetiva exige alternativas e resposta correta;
  - dissertativa exige número de linhas;
  - campos do tipo oposto são rejeitados.
- `numero_linhas` deve ser maior que zero.
- A lista de disciplinas verifica os tipos antes de executar operações de string.

Arquivos principais:

- `api/modelos/questao.py`
- `api/middlewares/questao_middleware.py`
- `api/controles/questao_controle.py`
- `api/DAOs/questao_dao.py`

### Provas

- O campo `questoes` recebe e armazena objetos completos, em vez de IDs de questões.
- `_id` e `ativo`, mesmo quando vierem da listagem do banco de questões, são descartados antes da persistência na prova.
- Questões com o mesmo enunciado são rejeitadas.
- Cada questão é validada novamente pelo modelo antes de ser incorporada à prova.
- O tipo de cada questão precisa corresponder ao tipo da prova.
- A disciplina de cada questão precisa corresponder ao código ou nome da disciplina da prova.
- A ordem das questões enviada pelo professor é preservada.
- O conteúdo incorporado inclui alternativas e `alternativa_correta` nas questões objetivas.
- A listagem de provas retorna as questões completas, incluindo o gabarito.
- A exclusão passou a ser lógica.
- A chave de coleção na resposta GET foi padronizada para `provas`.
- Parâmetros de filtro desconhecidos são rejeitados.

Arquivos principais:

- `api/modelos/prova.py`
- `api/services/prova_service.py`
- `api/DAOs/prova_dao.py`
- `api/controles/prova_controle.py`
- `servidor.py`

Compatibilidade: documentos antigos cujo campo `questoes` ainda contenha IDs precisam ser migrados ou recriados. O novo contrato exige que cada item seja um objeto de questão completo.

### Tratamento de erros e inicialização

- `resposta_erro_http`, erros de validação e erros internos agora usam chaves em português e formato consistente.
- `ValueError` e `TypeError` são transformados em HTTP 400.
- Stack traces continuam registrados no servidor, mas não são enviados no JSON.
- Erros internos retornam o código estável `INTERNAL_ERROR`.
- Erros HTTP, inclusive 404, retornam JSON.
- `app.py` não inicia o servidor automaticamente quando é importado; agora usa `if __name__ == "__main__"`.
- O cliente MongoDB é redefinido para `None` após o fechamento, permitindo uma conexão futura válida.

Arquivos principais:

- `api/utils/resposta_erro_http.py`
- `servidor.py`
- `app.py`
- `api/banco_de_dados/banco_de_dados.py`

### Documentação de payloads

Os JSONs de exemplo foram atualizados para refletir os nomes e regras efetivamente usados pelo código:

- professor representado por `usuario` e pelo campo `nome`;
- `serie` no lugar de `ano`;
- remoção de IDs gerados pelo servidor dos payloads de criação;
- remoção de `ativo` do cadastro de aluno e usuário;
- cinco objetos completos de questões no exemplo de prova, sem IDs e com gabarito;
- exemplos com valores que passam pelas validações.

Arquivos:

- `api/docs/jsons/alunos/aluno.json`
- `api/docs/jsons/disciplina.json`
- `api/docs/jsons/questao.json`
- `api/docs/jsons/prova.json`
- `api/docs/jsons/usuario/usuario_post.json`
- `api/docs/jsons/usuario/usuario_put.json`
- `api/docs/jsons/alunos/planilha_modelo.xlsx`

### Higiene do repositório

- Foi removido o único `.pyc` que estava rastreado pelo Git em `api/utils/__pycache__`.
- `api/.gitignore` passou a ignorar também o cache de `api/utils`.

Motivo: bytecode é gerado automaticamente, varia conforme a versão do Python e não deve participar das alterações de código-fonte.

## Testes criados

Foi criada uma suíte em `backend/tests` usando `unittest`, Flask Test Client, DAOs em memória e coleções Mongo simuladas.

Arquivos:

- `tests/fakes.py`: implementações em memória para os fluxos HTTP e services.
- `tests/test_fluxos_api.py`: alunos, usuários, disciplinas, questões, provas e planilha.
- `tests/test_daos.py`: projeções de consulta, matrícula e exclusões lógicas nos DAOs reais.
- `tests/test_erros_servidor.py`: contratos de erro 400/500 e ausência de stack trace na resposta.

Coberturas verificadas:

1. Cadastro de aluno persiste matrícula.
2. Listagem de alunos omite e-mail.
3. Exclusão de aluno é lógica e retorna 200.
4. Conversão de `ativo=false`.
5. Rejeição de filtro desconhecido.
6. Importação valida antes de escrever e usa upsert.
7. Planilha-modelo é aceita pelo importador.
8. Cadastro, login, listagem e atualização de usuário.
9. Senha não aparece na listagem.
10. Disciplina lista quantidade em vez das matrículas.
11. Filtros aninhados de professor.
12. Listagem de questões retorna o gabarito para o professor.
13. Middleware rejeita combinação incompatível de tipo de questão.
14. Prova valida e persiste questões completas sem IDs.
15. Listagem de prova retorna as questões completas e o gabarito.
16. DAOs usam exclusão lógica para disciplina, questão e prova.
17. Erros de validação retornam 400.
18. Erros internos não expõem stack ou mensagem original.

## Resultado das verificações

Comando executado:

```powershell
$env:PYTHONIOENCODING='utf-8'
python.exe -m unittest discover -s tests -v
```

Resultado final:

- 15 testes executados.
- 15 testes aprovados.
- 54 arquivos Python analisados sem erro de sintaxe.
- 8 arquivos JSON validados.
- Imports de `app` e `servidor` concluídos sem iniciar o servidor.
- `git diff --check` sem erros de whitespace.
- Planilha-modelo renderizada e verificada visualmente, sem erros de fórmula.

## Limites da verificação

- Os testes não conectaram ao MongoDB real e não alteraram a base existente.
- As operações PyMongo foram verificadas com coleções simuladas.
- JWT, CORS, HTTPS, rate limiting e configuração de produção ficaram fora do escopo solicitado.
- Não foi executada a integração com `sistema-correcao`.
- Provas antigas que armazenam somente IDs precisam ser migradas para o novo formato de questões incorporadas.
