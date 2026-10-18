# Listas de controle por turma na impressão

A tela `/provas/imprimir/{id}`, utilizada pelo processo pedagógico, inclui dois
documentos antes das provas de cada sala: **Planilha de notas** e **Relatório de
entrega**. Os modelos reproduzem a estrutura das fotos de referência, com os
logotipos já existentes, tabelas com bordas e linhas alternadas em cinza.

## Dados e organização

- A tela continua consultando os metadados da prova e
  `GET /provas/imprimir-provas/{id}`. Cada versão retorna matrícula, nome e
  `turma_aluno`, além do identificador individual e das questões.
- O campo cadastrado `turma` já deve conter série, letra e curso, por exemplo
  `1ºI - INFORMÁTICA`. O texto é utilizado integralmente, sem inferir curso nem
  criar campos ou coleções adicionais.
- `utils/listasTurma.js` agrupa somente alunos com versão individual retornada
  pela API. Ordena cada turma pelo nome completo em português e gera a chamada
  sequencial a partir de 1. Em nomes iguais, desempata pela matrícula.
- Nome/turma ausentes, turma fora da prova ou matrícula repetida interrompem a
  montagem com aviso para conferir os registros. Não é criada uma lista
  silenciosamente incompleta.
- A ordem de impressão é: planilha, relatório e provas daquela turma; depois,
  repete a sequência para a próxima sala. O cartão de cada aluno exibe a turma
  dele, não a relação de todas as turmas da prova.
- Não são alterados o QR Code, a ordem das questões nem o posicionamento das
  alternativas de cada versão.

## Modelos

`components/ListaTurma.vue` concentra os dois formatos:

| Documento | Identificação | Colunas e campos manuais |
|---|---|---|
| Planilha de notas | Instituição, título/ano, turma, disciplina, professor, data de aplicação e período letivo | Nº, matrícula, nome do aluno, assinatura e nota; rodapé com datas de entrega ao pedagógico/lançamento e assinatura do professor |
| Relatório de entrega | Título, período letivo, turma em faixa escura, disciplina e professor | Nº, matrícula, nome e assinatura do aluno ao receber a prova corrigida; assinatura do professor no rodapé |

Assinaturas, notas e datas de controle saem em branco. A data de aplicação da
planilha vem da prova-base; não é uma data de controle. Não há referência a A1,
avaliação dissertativa ou bimestre: as nomenclaturas são avaliação objetiva e
período letivo.

Cada página contém até 28 alunos, com cabeçalho e rodapé repetidos. A chamada
continua na página seguinte. As quebras separam documentos e turmas. Utilizar
A4, escala 100% e cabeçalhos/rodapés do navegador desativados, como nas provas.

## Escopo e validação

Gerar ou visualizar as listas não grava nada no banco nem confirma impressão.
A confirmação é feita no card da prova recebida, pelo botão ao lado da impressora
e pelo modal de confirmação, utilizando a rota existente. A prévia não contém
esse botão. A coluna de nota não
consome o resultado da correção; impressão automática de notas é outra etapa.

Os testes de `tests/listasTurma.test.js` cobrem agrupamento, ordenação, chamada,
campos vazios, duas variantes e paginação com 57 alunos. A integração na tela
de impressão é coberta em `tests/provas.test.js`; o retorno da turma no backend,
em `backend/tests/test_fluxos_api.py`.
