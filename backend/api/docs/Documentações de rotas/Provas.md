# Fluxo de provas

Documentação das rotas responsáveis pela criação da prova-base, seleção das
questões, geração das versões individuais, conclusão/envio ao pedagógico, montagem
para impressão, consulta, atualização e exclusão lógica.

## Endereço-base

```text
http://localhost:8080/api/v1/provas
```

## Autenticação

Atualmente, as rotas de provas não exigem token JWT.

## Resumo das rotas

| Método | Rota | Finalidade |
|---|---|---|
| `POST` | `/api/v1/provas/criar-prova` | Criar a prova-base sem questões |
| `PATCH` | `/api/v1/provas/{_id}/adicionar-questoes` | Salvar os IDs selecionados e gerar/preservar as versões dos alunos |
| `PATCH` | `/api/v1/provas/{_id}/enviar` | Concluir a prova, enviar ao pedagógico e encerrar a edição |
| `GET` | `/api/v1/provas/imprimir-provas/{_id}` | Montar as versões completas para impressão |
| `PATCH` | `/api/v1/provas/{_id}/confirmar-impressao` | Registrar a confirmação de impressão e definir o status Impressa |
| `POST` | `/api/v1/provas/corrigir-provas` | Corrigir cartões-resposta em lote |
| `GET` | `/api/v1/provas/` | Consultar provas ativas |
| `PUT` | `/api/v1/provas/{_id}` | Atualizar metadados antes de vincular questões; não altera status ou seleção |
| `DELETE` | `/api/v1/provas/{_id}` | Desativar uma prova |

---

# Visão geral do fluxo

1. O processo pedagógico cria uma prova-base por `/criar-prova`.
2. A prova é armazenada com `questoes: []` e status
   `Aguardando questões`.
3. O professor abre a base existente e apenas seleciona e ordena questões do banco.
   Não cria/edita questões nem altera metadados nessa tela.
4. O frontend envia somente IDs para `/adicionar-questoes`. A base fica `Em elaboração`.
5. A API cria configurações em `provas_x_alunos` para os alunos ativos. Repetir
   a mesma seleção, com versões completas, preserva os gabaritos individuais.
6. `PATCH /{_id}/enviar` verifica as versões e conclui a prova como
   `Enviada ao pedagógico`. A edição passa a ser bloqueada.
7. A listagem pedagógica mostra provas enviadas, não bases em elaboração,
   sem filtrar pelo nome ou registro do funcionário pedagógico como professor.
8. `/imprimir-provas/{_id}` usa as configurações individuais para retornar
   as questões completas e as alternativas posicionadas.

O sistema cria e corrige apenas provas objetivas. Outros tipos são rejeitados
com HTTP `400` na criação e atualização. As consultas retornam somente provas
objetivas, sem excluir registros antigos do banco.

---

# Estruturas armazenadas

## Prova-base

A coleção `provas` armazena somente os IDs das questões.

```json
{
  "_id": "66c4a6c22ce79c0f588b1621",
  "id_turma": [
    "Turma 2026 A",
    "Turma 2026 B"
  ],
  "professor": {
    "registro": 101,
    "nome": "Carlos Silva"
  },
  "disciplina": {
    "codigo_disciplina": "MAT",
    "nome_disciplina": "Matemática"
  },
"status": "Em elaboração",
  "tipo": "Objetiva",
  "serie": 3,
  "periodo_letivo": "1º período letivo",
  "data_de_aplicacao": "2026-08-20",
  "quantidade_questoes": 3,
  "questoes": [
    "66c49f5a2ce79c0f588b1601",
    "66c49f5a2ce79c0f588b1602"
  ],
  "ativo": true
}
```

O campo `ativo` existe no banco, mas é omitido nas respostas de consulta.
Os campos internos `operacao_em_andamento` e `geracao_pendente` controlam
concorrência e recuperação. Não fazem parte do corpo enviado pelo frontend
nem das provas retornadas nas respostas públicas.

## Versão individual: ProvaXAluno

A coleção `provas_x_alunos` armazena uma configuração por prova e matrícula.

```json
{
  "matricula_aluno": 50280715,
  "id_prova": "66c4a6c22ce79c0f588b1621",
  "questoes": [
    {
      "id_questao": "66c49f5a2ce79c0f588b1602",
      "posicao_alternativa_correta": 4
    },
    {
      "id_questao": "66c49f5a2ce79c0f588b1601",
      "posicao_alternativa_correta": 2
    }
  ]
}
```

Não existe um campo separado com o número da questão. A posição do item no
vetor `questoes` determina sua numeração na versão daquele aluno.

A combinação abaixo é única no banco:

```text
id_prova + matricula_aluno
```

Assim, um aluno pode possuir versões de provas diferentes, mas não pode possuir
dois documentos para a mesma prova.

---

# Regras dos campos da prova

## Identificador

`_id` é gerado pelo MongoDB e convertido para string nas respostas. Normalmente
é representado por 24 caracteres hexadecimais.

O middleware das rotas com ID verifica a presença do parâmetro. A validação do
formato ocorre quando o DAO tenta convertê-lo para `ObjectId`. A rota de
impressão consulta `provas_x_alunos` diretamente pelo valor textual recebido.

## Turmas

`id_turma` aceita uma string:

```json
{
  "id_turma": "Turma 2026 A"
}
```

Também aceita uma lista:

```json
{
  "id_turma": [
    "Turma 2026 A",
    "Turma 2026 B"
  ]
}
```

Cada turma deve:

- ser uma string;
- ter os espaços externos removidos.

Limitações atuais:

- a API não verifica a existência das turmas;
- turmas repetidas não são rejeitadas pelo modelo;
- uma lista vazia não é rejeitada pelo modelo.

Na geração das versões individuais, turmas repetidas são desconsideradas e a
consulta inclui somente alunos cujo `ativo` não seja `false`.

## Professor

Na criação da prova-base, o professor deve conter registro e nome:

```json
{
  "professor": {
    "registro": 101,
    "nome": "Carlos Silva"
  }
}
```

O registro deve ser inteiro. O nome:

- deve ser uma string;
- deve possuir ao menos 5 caracteres;
- deve conter nome e sobrenome;
- exige ao menos 3 caracteres em cada parte;
- é normalizado com iniciais maiúsculas.

A criação não verifica se o professor existe ou está ativo no fluxo de usuários.

Na rota `PUT`, o registro também é exigido pelo service e retornado na resposta.
Não é permitido trocar o professor depois de vincular questões.

## Disciplina

```json
{
  "disciplina": {
    "codigo_disciplina": "MAT",
    "nome_disciplina": "Matemática"
  }
}
```

`codigo_disciplina` deve ser uma string e tem seus espaços externos removidos.
`nome_disciplina` deve ser uma string com ao menos 3 caracteres e é normalizado
com iniciais maiúsculas.

A criação não consulta o fluxo de disciplinas. Entretanto, código e nome são
utilizados para verificar a compatibilidade das questões selecionadas.

## Tipo

Valores aceitos:

```text
Objetiva
```

O valor é normalizado com espaços externos removidos e iniciais maiúsculas.
Todas as questões selecionadas devem possuir o mesmo tipo da prova.

Todas as provas geram documentos em `provas_x_alunos` ao receberem questões,
quando há alunos ativos nas turmas vinculadas.

## Status

O status é uma string sem lista fixa de valores.

Na criação, não deve ser enviado. A API define automaticamente:

```text
Aguardando questões
```

O fluxo usa `Aguardando questões` na criação, `Em elaboração` após salvar a
seleção e `Enviada ao pedagógico` ao concluir. Apenas os dois primeiros permitem
edição. Após a confirmação de impressão, o status passa para `Impressa`.
Status posteriores, como `Impressa` e `Corrigida`, também são
somente leitura para a montagem. O modelo continua aceitando strings, sem enum.
`PUT` deve preservar o status; somente a rota dedicada realiza o envio.

## Série

Deve ser um número inteiro maior que zero.

## Período letivo

Deve ser uma string. Os espaços externos são removidos. O formulário apresenta
do `1º período letivo` ao `4º período letivo`, mas o backend não impõe lista fixa.
O campo é `periodo_letivo` tanto na API quanto no MongoDB. Ele é obrigatório na
criação e está presente nas respostas e nos filtros de consulta. Não há conversão
de nomenclaturas anteriores; novas provas devem usar diretamente esse campo.

## Data de aplicação

Deve ser uma string. O formato recomendado é:

```text
AAAA-MM-DD
```

Atualmente, a API não valida o formato, a existência da data no calendário ou
se ela está no passado ou no futuro.

## Questões da prova-base

O campo `questoes` é uma lista de IDs em formato string.

Na criação, ele é gerenciado pela API e começa vazio. Em
`/adicionar-questoes`, deve conter de 2 a 10 IDs, sem ultrapassar a quantidade
definida na prova-base.

## Quantidade de questões

`quantidade_questoes` é obrigatória na criação: um inteiro entre **2 e 10**.
Strings, booleanos, decimais, valores nulos e números fora desse intervalo
retornam `400`. O valor é armazenado na prova e devolvido nas respostas de
criação, consulta e atualização; ele não altera o formato de envio dos IDs.

O professor pode salvar seleções parciais de pelo menos duas questões. Para
concluir e enviar, precisa selecionar **exatamente** a quantidade definida pelo
processo pedagógico. Uma seleção acima desse total é rejeitada sem alterar o
banco ou os gabaritos. Após vincular questões, a quantidade não pode ser alterada
pelo PUT, assim como os demais metadados. Se omitida no PUT, o valor salvo é
preservado, não apagado.

Provas antigas sem esse campo (ou com valor `null`) mantêm a regra anterior de
2 a 10 questões, sem exigir total exato e sem migração automática dos dados.
Impressão, confirmação de impressão e correção também conferem a quantidade
quando definida; registros incompatíveis não são impressos/corrigidos.

Regras aplicadas na seleção e novamente antes de concluir:

- a estrutura deve ser uma lista;
- deve haver de 2 a 10 questões, sem ultrapassar `quantidade_questoes`;
- para concluir, deve haver exatamente `quantidade_questoes`, quando definida;
- cada ID deve ser uma string não vazia;
- espaços externos são removidos;
- IDs repetidos são rejeitados;
- todas as questões devem existir e estar ativas;
- o tipo da questão deve ser igual ao tipo da prova;
- a questão deve possuir o código ou o nome da disciplina da prova;
- enunciado e cinco alternativas distintas devem estar preenchidos (texto ou imagem);
- os IDs das alternativas devem ser distintos e a correta deve apontar para um deles.

A comparação da disciplina ignora maiúsculas, minúsculas e espaços externos.

Exemplo válido com duas questões (pode ser uma seleção parcial):

```json
{
  "questoes": [
    "66c49f5a2ce79c0f588b1601",
    "66c49f5a2ce79c0f588b1602"
  ]
}
```

Não existe quantidade mínima de cinco questões: o mínimo é duas.
Seleções acima de dez são rejeitadas com HTTP `400` antes de salvar a seleção
ou gerar versões individuais. O envio também revalida esse limite, inclusive
para provas antigas. Os registros existentes não são truncados nem apagados.
No frontend, o contador mostra a quantidade selecionada e uma mensagem informa
o total definido pelo pedagógico. Ao atingir esse total (ou dez para bases
antigas), a adição é bloqueada. Uma seleção em lote que excederia o máximo não é
adicionada, e um aviso orienta a selecionar individualmente as questões desejadas.

---

# Criar prova-base

## Rota

```http
POST /api/v1/provas/criar-prova
```

## Cabeçalho

```http
Content-Type: application/json
```

## Corpo

```json
{
  "prova": {
    "id_turma": [
      "Turma 2026 A",
      "Turma 2026 B"
    ],
    "professor": {
      "registro": 101,
      "nome": "Carlos Silva"
    },
    "disciplina": {
      "codigo_disciplina": "MAT",
      "nome_disciplina": "Matemática"
    },
    "tipo": "Objetiva",
    "serie": 3,
    "periodo_letivo": "1º período letivo",
    "data_de_aplicacao": "2026-08-20",
    "quantidade_questoes": 3
  }
}
```

Todos os campos apresentados são obrigatórios.

Os campos gerenciados abaixo não devem ser enviados:

```text
_id
ativo
status
questoes
```

Se qualquer um deles estiver presente dentro de `prova`, o middleware retorna
erro `400`. Outros campos desconhecidos não são persistidos pelo service atual.

## Resultado da criação

A API cria automaticamente:

```json
{
  "status": "Aguardando questões",
  "questoes": [],
  "ativo": true
}
```

## Resposta de sucesso

Código: `201 Created`.

```json
{
  "sucesso": true,
  "mensagem": "Prova criada com sucesso",
  "data": {
    "prova": {
      "_id": "66c4a6c22ce79c0f588b1621",
      "id_turma": [
        "Turma 2026 A",
        "Turma 2026 B"
      ],
      "professor": {
        "registro": 101,
        "nome": "Carlos Silva"
      },
      "disciplina": {
        "codigo_disciplina": "MAT",
        "nome_disciplina": "Matemática"
      },
      "status": "Aguardando questões",
      "tipo": "Objetiva",
      "serie": 3,
      "periodo_letivo": "1º período letivo",
      "data_de_aplicacao": "2026-08-20",
      "quantidade_questoes": 3,
      "questoes": []
    }
  }
}
```

## Erros principais

Corpo sem a chave `prova`:

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'prova' é obrigatório!"
  }
}
```

Campo obrigatório ausente, por exemplo `tipo`:

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'tipo' é obrigatório!"
  }
}
```

Valores que não atendem às regras dos modelos retornam `400` com a mensagem
geral `Dados inválidos` e o detalhe da validação.

---

# Adicionar questões

## Rota

```http
PATCH /api/v1/provas/{_id}/adicionar-questoes
```

A operação substitui o vetor atual da prova-base, preservando a ordem enviada.
Ela não acrescenta itens ao vetor existente. Aceita somente o campo `questoes`
com strings de IDs; objetos completos e metadados adicionais são rejeitados.
Provas concluídas retornam `409` e não têm suas versões alteradas.

## Corpo

```json
{
  "prova": {
    "questoes": [
      "66c49f5a2ce79c0f588b1601",
      "66c49f5a2ce79c0f588b1602"
    ]
  }
}
```

## Comportamento para provas objetivas

Depois de validar e atualizar a prova-base, a API:

1. busca os alunos ativos das turmas da prova;
2. elimina matrículas repetidas;
3. embaralha a ordem das questões separadamente para cada aluno;
4. gera `posicao_alternativa_correta` entre `1` e `5` para cada questão;
5. sincroniza os documentos na coleção `provas_x_alunos`.

Para duas ou mais questões, a versão do aluno não permanece acidentalmente na
mesma ordem da prova-base. Alunos diferentes ainda podem receber a mesma ordem
por coincidência.

Correspondência da posição da alternativa correta:

```text
1 = A
2 = B
3 = C
4 = D
5 = E
```

As alternativas ainda não são reorganizadas nesta rota. Apenas a posição futura
é armazenada.

## Sincronização e repetição da rota

A combinação `id_prova + matricula_aluno` é atualizada com `upsert`. Portanto,
repetir a rota não duplica documentos.

Se a lista e sua ordem não mudaram, e existem versões para todos os alunos ativos
com as mesmas questões, a API reutiliza as configurações: não embaralha novamente.
A resposta informa `versoes_regeneradas: false` e a quantidade já disponível.

Seleção ou ordem diferente, mudança nos alunos ativos, versões ausentes ou
inconsistentes exigem geração/sincronização, ainda durante a elaboração.
Antes de gerar, os IDs e `geracao_pendente: true` são gravados juntos na prova-base.
Esse indicador só é removido depois que toda a sincronização termina com sucesso.
Se o salvamento anterior falhou depois de gravar os IDs, repetir o PATCH refaz
a geração, mesmo que os registros presentes pareçam completos, sem criar outra
prova-base. Enquanto houver geração pendente, a prova não pode ser enviada.

Versões de alunos que não pertencem mais às turmas são removidas. Se nenhuma
matrícula ativa for encontrada, todas as versões individuais daquela prova são
removidas e `provas_alunos_geradas` retorna `0`.

Documentos pertencentes a outras provas não são alterados.

## Concorrência entre geração e conclusão

Seleção/geração, envio, atualização de metadados e exclusão lógica usam a mesma
reserva por prova, adquirida com uma atualização atômica no MongoDB. Somente uma
operação pode possuir a reserva; a prova é relida depois da aquisição. O token
da reserva também é exigido nas escritas e na liberação, impedindo que outra
requisição altere ou libere a operação em andamento.

Uma requisição concorrente para a mesma prova recebe HTTP `409`, com orientação
para aguardar e tentar novamente. Ela não fica em uma fila nem inicia geração.
Provas diferentes continuam podendo ser processadas em paralelo. A proteção
fica no banco e não depende de todas as requisições usarem o mesmo processo Flask.

A reserva cobre a validação, a gravação dos IDs e toda a geração das versões;
no envio, cobre a conferência das versões e a mudança de status. Assim, gabaritos
anteriores não podem habilitar a conclusão durante uma nova geração, inclusive
quando só a ordem dos mesmos IDs foi alterada.

A reserva é liberada ao terminar a operação ou ao ocorrer uma exceção tratável.
Ela não expira automaticamente: se o processo for encerrado abruptamente antes
da liberação, será necessária recuperação administrativa da reserva no banco,
apenas após confirmar que a operação anterior não pode mais executar. Não remova
`geracao_pendente` nessa recuperação; se existir, repita o salvamento da seleção
para refazer a geração antes de enviar. A ausência de expiração evita liberar
uma geração lenta ainda em execução e permitir outra escrita sobre seus resultados.

## Resposta de sucesso

Código: `200 OK`.

```json
{
  "sucesso": true,
  "mensagem": "Questões adicionadas com sucesso",
  "data": {
    "prova": {
      "_id": "66c4a6c22ce79c0f588b1621",
      "status": "Em elaboração",
      "questoes": [
        "66c49f5a2ce79c0f588b1601",
        "66c49f5a2ce79c0f588b1602"
      ]
    },
    "provas_alunos_geradas": 32,
    "versoes_regeneradas": true
  }
}
```

A resposta inclui a prova-base completa (metadados, ID, status e seleção).
O exemplo acima destaca apenas ID, status e questões. `provas_alunos_geradas`
representa a quantidade disponível, inclusive quando as versões foram reutilizadas.

Se não houver alunos ativos nas turmas vinculadas, `provas_alunos_geradas` é `0`.

## Erros principais

| Situação | Código | Mensagem principal |
|---|---:|---|
| Prova inexistente, inativa ou ID inválido | `404` | `Prova não encontrada` |
| Lista vazia | `400` | `Número de questões insuficiente` |
| Mais de dez questões | `400` | `Limite de questões excedido` |
| `questoes` não é lista | `400` | `Questões inválidas` |
| ID não é string ou está vazio | `400` | `Id de questão inválido` |
| IDs repetidos | `400` | `Questões repetidas` |
| Questão inexistente ou inativa | `400` | `Questão não encontrada` |
| Tipo incompatível | `400` | `Tipo de questão incompatível` |
| Disciplina incompatível | `400` | `Disciplina incompatível` |
| Enunciado, alternativas ou correta inválidos no banco | `400` | `Questão incompleta` |
| Prova concluída | `409` | `Prova concluída não pode ser editada` |
| Outra operação na mesma prova | `409` | `Há outra operação em andamento nesta prova. Aguarde e tente novamente` |

Exemplo para questão inexistente:

```json
{
  "sucesso": false,
  "mensagem": "Questão não encontrada",
  "erro": {
    "mensagem": "Uma ou mais questões não existem ou estão inativas"
  }
}
```

Observação: a prova-base é atualizada antes da geração das versões individuais.
O fluxo atual não utiliza transação entre as duas coleções.

---

# Concluir e enviar ao processo pedagógico

```http
PATCH /api/v1/provas/{_id}/enviar
```

Sem corpo JSON. A rota utiliza os IDs já salvos na prova-base, não recebe
objetos de questões e não gera novos gabaritos.

O service verifica a existência da prova, a integridade das questões e versões
individuais completas para os alunos ativos. Se não houver versões, retorna
`409` e orienta conferir os alunos e salvar a seleção novamente.
Se a seleção não tiver exatamente `quantidade_questoes`, quando definida,
retorna `400`, preservando a seleção parcial e o status de elaboração.
Se houver uma operação em andamento, retorna `409` sem concluir a prova.
Uma geração anterior não finalizada também retorna `409` (`Geração de versões
pendente`) e exige salvar novamente antes do envio. Essas verificações ocorrem
sob a mesma reserva usada pela geração, impedindo alterações dos gabaritos entre
a conferência das versões e a conclusão.

Sucesso: `200`, com `data.prova` (mesmo ID e status `Enviada ao pedagógico`)
e `data.provas_alunos_geradas` (quantidade disponível). Repetir o envio de uma
prova já enviada é idempotente: preserva status e gabaritos.

Após enviar, `PUT`, `PATCH /adicionar-questoes` e `DELETE` retornam `409`.
O editor exibe apenas visualização, sem ações de seleção, reordenação ou edição.
Questões vinculadas a provas concluídas também não podem ser alteradas/excluídas
pelo fluxo do banco, impedindo que o conteúdo e o gabarito mudem indiretamente.

---

# Confirmar impressão

```http
PATCH /api/v1/provas/{_id}/confirmar-impressao
```

Sem corpo. O processo pedagógico usa o botão `Confirmar impressão realizada`
depois de efetivamente imprimir. Abrir a prévia, consultar o GET ou fechar o
diálogo do navegador não confirma a impressão, pois o diálogo também pode ser
cancelado. O status só muda no frontend após sucesso da gravação no backend.

Retorna `200 OK`, com `data.prova` contendo a prova e `status: "Impressa"`.
Repetir a confirmação de uma prova já impressa é idempotente. A operação exige
uma base ativa, enviada, sem geração pendente e com versões individuais válidas.
Prova inexistente/inativa retorna `404`; estado incompatível ou versões ausentes
retorna `409`. Usa a mesma reserva exclusiva das demais alterações da prova.

Não altera questões, IDs, QR Codes nem gabaritos. Reimprimir continua permitido,
e uma prova `Corrigida` não volta para `Impressa`. O status impresso não reabre
a edição. A correção ainda não persiste notas nem define `Corrigida` automaticamente.

No frontend pedagógico, as abas são exclusivas: `Provas Recebidas` mostra
`Enviada ao pedagógico`, `Provas Impressas` mostra `Impressa` e `Provas Corrigidas`
mostra `Corrigida`. Para o professor, provas impressas continuam na aba de enviadas.

---

# Imprimir provas

## Rota

```http
GET /api/v1/provas/imprimir-provas/{_id}
```

A rota não recebe corpo JSON e não altera documentos no banco.

Antes de consultar `provas_x_alunos`, a API verifica a prova-base pelo ID:
ela deve existir, estar ativa (`ativo` diferente de `false`) e ser objetiva.
Base inexistente, inativa, de tipo não suportado ou ID inválido retorna HTTP
`404` (`Prova não encontrada`), mesmo que ainda existam versões individuais.
Essas versões não são apagadas nem alteradas pela impressão. Uma base válida
e concluída sem versões continua retornando `200` com `provas_alunos: []`.
Bases ainda em `Aguardando questões` ou `Em elaboração` retornam `409`:
`Conclua e envie a prova antes de imprimir`.

## Montagem

1. Busca em `provas_x_alunos` todos os documentos com o `id_prova` informado.
2. Ordena as versões por `matricula_aluno`.
3. Reúne os IDs necessários e busca as questões ativas em uma única consulta.
4. Para cada aluno, percorre as questões na ordem armazenada em sua versão.
5. Cria uma cópia de cada questão completa.
6. Separa a alternativa correta, embaralha as incorretas e reinsere a correta
   na posição definida.

A conversão usada é:

```python
indice = posicao_alternativa_correta - 1
```

```text
Posição 1 -> índice 0 -> A
Posição 2 -> índice 1 -> B
Posição 3 -> índice 2 -> C
Posição 4 -> índice 3 -> D
Posição 5 -> índice 4 -> E
```

As alternativas incorretas são embaralhadas usando uma semente derivada do ID
da versão individual e do ID da questão. Repetir a impressão mantém a mesma
ordem, sem gravar novos dados ou regenerar gabaritos. A ordem das questões e a
posição da correta permanecem definidas pelo documento do aluno.

O campo `alternativa_correta` continua presente no objeto completo retornado.

Cada versão também retorna `id_prova_aluno`, o `_id` de `provas_x_alunos`.
O frontend deve inserir exatamente esse identificador textual no QR Code do
cartão-resposta; ele não deve conter apenas a matrícula ou o ID da prova-base.

O campo `nome_aluno` vem do cadastro associado à matrícula e preenche o campo
`Nome` do cartão. A linha inferior `Nome do Aluno por Extenso` permanece vazia
para preenchimento manual. Os nomes são consultados em lote, sem alterar as
versões individuais; se o cadastro não existir, o campo retorna uma string vazia.

## Resposta de sucesso

Código: `200 OK`.

```json
{
  "sucesso": true,
  "mensagem": "Provas montadas com sucesso",
  "data": {
    "id_prova": "66c4a6c22ce79c0f588b1621",
    "provas_alunos": [
      {
        "id_prova_aluno": "66c4a6c22ce79c0f588b1699",
        "matricula_aluno": 50280715,
        "nome_aluno": "José da Silva",
        "questoes": [
          {
            "_id": "66c49f5a2ce79c0f588b1602",
            "assunto": "Álgebra",
            "disciplina": [
              "mat",
              "matemática"
            ],
            "tipo_questao": "Objetiva",
            "dificuldade": "Médio",
            "autor": "Carlos Silva",
            "enunciado": "Quanto é 2 + 2?",
            "professor": {
              "nome": "Carlos Silva"
            },
            "alternativas": [
              {"id": "alt-2", "texto": "3"},
              {"id": "alt-3", "texto": "5"},
              {"id": "alt-4", "texto": "6"},
              {"id": "alt-1", "texto": "4"},
              {"id": "alt-5", "texto": "7"}
            ],
            "alternativa_correta": "alt-1"
          }
        ]
      }
    ]
  }
}
```

No exemplo, a alternativa correta está na posição `4`, índice `3`, letra `D`.

## Nenhuma versão encontrada

Uma base existente, ativa, objetiva e concluída, mas sem versões individuais,
retorna `200 OK`. Base inexistente ou ID inválido retorna `404`, não lista vazia:

```json
{
  "sucesso": true,
  "mensagem": "Provas montadas com sucesso",
  "data": {
    "id_prova": "66c4a6c22ce79c0f588b1621",
    "provas_alunos": []
  }
}
```

## Erros principais

| Situação | Código | Mensagem principal |
|---|---:|---|
| Prova-base inexistente, inativa, não objetiva ou ID inválido | `404` | `Prova não encontrada` |
| Prova ainda editável | `409` | `Conclua e envie a prova antes de imprimir` |
| Questão referenciada inexistente ou inativa | `404` | `Questão não encontrada` |
| Questão objetiva sem alternativas válidas | `400` | `Questão inválida` |
| ID da alternativa correta não localizado | `400` | `Questão inválida` |
| Posição não inteira ou fora do vetor | `400` | `Posição da alternativa correta inválida` |

## Integração de impressão no frontend

O processo pedagógico usa o botão de impressão no card recebido para abrir
`/provas/imprimir/{id}`. A tela consulta os metadados da base e esta rota de
impressão; não monta versões a partir da listagem genérica de questões.
Ela exibe todas as versões, com matrícula, questões e alternativas na ordem
retornada. A renderização reutiliza `PreviewProva.vue` e o template local.

`CartaoResposta.vue` utiliza o desenho do modelo anexado, armazenado no frontend
em `src/assets/templates/cartao-resposta.png`, e sobrepõe metadados e o QR Code
gerado localmente pela biblioteca `qrcode`. O conteúdo do QR é exclusivamente
`id_prova_aluno`. A área de nome do aluno permanece em branco para preenchimento.

O cartão possui proporção `1200 × 286`, a mesma da normalização do leitor.
A grade permanece com **dez colunas por cinco linhas**, independentemente da
quantidade de questões. Preencher todo o retângulo somente nas primeiras N
colunas e deixar as demais em branco. A região lida continua em X de 13,7% a
53,6% e Y de 40% a 88%; o QR fica fora dessa região. Para corrigir, recortar o
cartão completo, incluindo seu contorno e QR, sem incluir o corpo da prova.

O botão `Imprimir provas` aguarda fontes e imagens antes de abrir a impressão
nativa do navegador. Usar papel A4, escala 100% e desativar os cabeçalhos e rodapés
do navegador. Cada aluno começa em uma página nova; questões longas podem
continuar em páginas adicionais.

No MVP não foi criado um novo status de impressão: a conclusão já bloqueia
alteração/exclusão da prova, regeneração de versões e alteração/exclusão das
questões vinculadas. Exigir conclusão antes de imprimir reaproveita essa
proteção, inclusive se o usuário cancelar o diálogo de impressão.

Se uma questão estiver ausente, a rota interrompe toda a montagem para não
entregar provas incompletas.

---

# Corrigir provas

`POST /api/v1/provas/corrigir-provas`

Recebe `multipart/form-data` com o campo repetido `imagens`. Cada arquivo deve
conter um único cartão-resposta já recortado, incluindo o QR Code. São aceitos
de 1 a 50 arquivos, até 5 MiB por imagem. O servidor limita o corpo total das
requisições a 50 MiB, incluindo o multipart.

```sh
curl -X POST http://localhost:8080/api/v1/provas/corrigir-provas \
  -F "imagens=@cartao-aluno-1.png" \
  -F "imagens=@cartao-aluno-2.png"
```

O endereço acima é ilustrativo: utilize a porta configurada na API principal.
No Windows, utilize `curl.exe` para evitar o alias do PowerShell.

## Integração e lógica

1. A API envia cada arquivo ao microserviço em `POST /processar`, no campo
   multipart `imagem`, sem gravar imagens em disco.
2. O microserviço retorna `qrcode` e `respostas`, com chaves textuais começando
   em `"1"`. O QR Code deve conter exatamente o `_id` de `provas_x_alunos`,
   disponibilizado na impressão como `id_prova_aluno`.
3. A API busca o registro individual e valida a prova-base usando seu campo
   `id_prova` (não o ID do QR Code). A base deve existir, estar ativa e ser
   objetiva. Vínculo ausente/inválido ou base indisponível gera erro individual
   `404` (`Prova-base não encontrada ou inativa`), sem calcular uma nota.
   Depois dessa validação, busca o nome do aluno pela matrícula. A ordem do vetor
   `questoes` define a numeração; `posicao_alternativa_correta` de 1 a 5 define
   A a E, respectivamente. Não é utilizado o gabarito da ordem original.
4. Todas as questões têm o mesmo peso: `nota_prova = acertos / total * 10`,
   arredondada para duas casas. `null` conta como erro. Uma resposta omitida
   pelo microserviço é falha de integração, não uma questão em branco.

O leitor atual possui dez posições. A correção aceita provas de 1 a 10 questões,
ignora posições excedentes em provas menores e rejeita provas maiores. As rotas
de seleção e envio aplicam o mesmo limite; a criação da prova-base continua sem
questões. A impressão não altera nem remove registros antigos acima do limite.

## Resposta

O lote retorna `200 OK`, inclusive quando há falhas individuais. O frontend deve
examinar tanto `resultados` quanto `erros`. `indice` começa em zero e identifica
o arquivo na ordem enviada; cada lista mantém essa ordem.

```json
{
  "sucesso": true,
  "mensagem": "Correções processadas",
  "data": {
    "resultados": [{
      "indice": 0,
      "arquivo": "cartao-aluno-1.png",
      "id_prova_aluno": "66c4a6c22ce79c0f588b1699",
      "matricula": 50280715,
      "nome": "Carlos Silva",
      "nota_prova": 6.67,
      "gabarito_aluno": {"1": "A", "2": "D", "3": null},
      "gabarito_correto": {"1": "A", "2": "D", "3": "E"}
    }],
    "erros": [{
      "indice": 1,
      "arquivo": "cartao-aluno-2.png",
      "codigo": 422,
      "mensagem": "QR Code não encontrado ou inválido"
    }]
  }
}
```

Falhas individuais: `404` para registro/aluno inexistente ou prova-base
indisponível (incluindo versões órfãs de provas desativadas), `422` para cartão ou
gabarito incompatível, `502` para falha de comunicação/resposta inválida,
`504` para timeout, `503` para fila ocupada e `500` para falha interna.
O campo `codigo` não altera o status HTTP do lote.
Uma base inválida não interrompe a correção das imagens válidas do mesmo lote.
Ausência de arquivos, arquivos vazios ou mais de 50 arquivos geram HTTP `400`;
imagem ou corpo acima do limite gera HTTP `413`.

Nenhuma nota, imagem, resposta ou alteração de status é persistida nesta etapa.

## Configuração e concorrência

Instale o cliente HTTP no ambiente da API principal:
`pip install -r requirements-correcao.txt`.

| Variável de ambiente | Padrão | Finalidade |
| --- | --- | --- |
| `CORRECAO_URL` | `http://127.0.0.1:5000` | URL-base do microserviço, sem `/processar` |
| `CORRECAO_TIMEOUT` | `30` | Timeout de leitura em segundos; conexão tem limite de 5 segundos |
| `CORRECAO_CONCORRENCIA` | `8` | Máximo de tarefas simultâneas por processo da API |

Um executor compartilhado permite chamadas concorrentes, com até duas vezes
o limite de concorrência em tarefas admitidas (executando ou aguardando).
Cada lote submete no máximo o limite de concorrência por vez. Se não houver
vaga em um segundo, aquele arquivo recebe erro `503` e pode ser reenviado.
As conexões HTTP são reutilizadas por worker, com sessões separadas.

A requisição HTTP aguarda o fim do lote; não há fila persistente, identificador
de job ou consulta posterior. A concorrência é nas chamadas ao microserviço,
não uma transformação do Flask em aplicação assíncrona. Para requisições
simultâneas, ambos os serviços precisam de servidores com capacidade de
concorrência. A quantidade de correções por segundo depende do leitor, CPU,
tamanho das imagens e configuração dos servidores; não há garantia de taxa.

---

# Consultar provas

## Rota

```http
GET /api/v1/provas/
```

A rota não recebe corpo JSON e retorna somente provas cujo `ativo` não seja
`false`.

## Resposta

```json
{
  "sucesso": true,
  "mensagem": "Executado com sucesso",
  "data": {
    "provas": [
      {
        "_id": "66c4a6c22ce79c0f588b1621",
        "id_turma": "Turma 2026 A",
        "professor": {
          "registro": 101,
          "nome": "Carlos Silva"
        },
        "disciplina": {
          "codigo_disciplina": "MAT",
          "nome_disciplina": "Matemática"
        },
"status": "Em elaboração",
        "tipo": "Objetiva",
        "serie": 3,
        "periodo_letivo": "1º período letivo",
        "data_de_aplicacao": "2026-08-20",
        "questoes": [
          "66c49f5a2ce79c0f588b1601"
        ]
      }
    ]
  }
}
```

Sem resultados, a API retorna `200 OK` e `provas: []`.

## Filtros

| Parâmetro | Conversão | Campo no MongoDB |
|---|---|---|
| `id` | string | `_id` |
| `id_turma` | string | `id_turma` |
| `codigo_disciplina` | string | `disciplina.codigo_disciplina` |
| `nome_disciplina` | string | `disciplina.nome_disciplina` |
| `nome` | string | `professor.nome` |
| `registro` | inteiro | `professor.registro` |
| `status` | string | `status` |
| `tipo` | string | `tipo` |
| `serie` | inteiro | `serie` |
| `periodo_letivo` | string | `periodo_letivo` |
| `data_de_aplicacao` | string | `data_de_aplicacao` |

Exemplos:

```http
GET /api/v1/provas/?id=66c4a6c22ce79c0f588b1621
GET /api/v1/provas/?registro=101
GET /api/v1/provas/?id_turma=Turma%202026%20A
GET /api/v1/provas/?codigo_disciplina=MAT&tipo=Objetiva&serie=3
```

Os filtros são combinados com condição lógica `E` e usam correspondência exata.
No MongoDB, consultar uma string em `id_turma` também encontra documentos em que
o campo é uma lista contendo essa string.

Parâmetros vazios são ignorados. Um parâmetro desconhecido retorna `400`. Um ID
com formato inválido retorna uma lista vazia. Um valor não inteiro em `serie` ou `registro`
também retorna `400`.

O frontend do processo pedagógico cria a prova-base pelo formulário da tela de
provas, enviando apenas os metadados para `POST /criar-prova`. O `_id` retornado
identifica a base criada. O professor consulta as provas atribuídas a ele
com `registro`, em vez de usar o nome, e utiliza esse mesmo ID para abrir o
editor, sem recriação. A listagem pedagógica oculta a base até seu envio pelo
professor. As questões são selecionadas em uma etapa posterior; a criação da base
não gera registros de `provaXaluno`.

---

# Atualizar prova

```http
PUT /api/v1/provas/{_id}
```

Mantida para atualização dos metadados da base antes de vincular questões.
O frontend de seleção não utiliza essa rota: envia apenas IDs no PATCH.

O corpo completo deve conter os metadados, professor com registro e nome,
`questoes` igual à seleção já persistida e `status` igual ao atual.
Não é possível concluir nem alterar a seleção por PUT (`400`).
Após vincular questões, alterações dos metadados retornam `409`, para não
desalinhar turmas, disciplina e versões individuais. Após concluir, qualquer
atualização retorna `409`. Prova inexistente/inativa/ID inválido retorna `404`.

Exemplo para uma base ainda sem questões:

```json
{
  "prova": {
    "id_turma": "Turma 2026 B",
    "professor": { "registro": 101, "nome": "Carlos Silva" },
    "disciplina": { "codigo_disciplina": "MAT", "nome_disciplina": "Matemática" },
    "tipo": "Objetiva",
    "serie": 3,
    "periodo_letivo": "1º período letivo",
    "data_de_aplicacao": "2026-08-22",
    "status": "Aguardando questões",
    "questoes": []
  }
}
```

Sucesso: `200`, com `data.prova` contendo os metadados, registro/nome do professor,
status, questões e o mesmo ID. A rota não gera versões individuais.

---

# Excluir prova

## Rota

```http
DELETE /api/v1/provas/{_id}
```

A exclusão é lógica. A API altera:

Permitida somente antes da conclusão. Provas concluídas retornam `409`.

```json
{
  "ativo": false
}
```

Ela não remove o documento da coleção `provas` e não remove as versões
existentes em `provas_x_alunos`.

## Sucesso

Código: `200 OK`.

```json
{
  "sucesso": true,
  "mensagem": "Excluído com sucesso",
  "data": null
}
```

## Prova inexistente, inativa ou ID inválido

Código: `404 Not Found`.

```json
{
  "sucesso": false,
  "mensagem": "Prova não encontrada",
  "erro": null
}
```

---

# Formato geral das respostas

## Sucesso

```json
{
  "sucesso": true,
  "mensagem": "Descrição do resultado",
  "data": {}
}
```

## Erro do middleware ou regra de negócio

```json
{
  "sucesso": false,
  "mensagem": "Descrição do erro",
  "erro": {
    "mensagem": "Detalhes do erro"
  }
}
```

## Erro de modelo

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Descrição da validação"
  }
}
```

## Erro interno

Código: `500 Internal Server Error`.

```json
{
  "sucesso": false,
  "mensagem": "Ocorreu um erro interno no servidor",
  "erro": {
    "codigo": "INTERNAL_ERROR"
  }
}
```

---

# Observações do estado atual

- Não há autenticação nas rotas de provas.
- O status não possui enumeração fixa.
- A API aceita provas com uma única questão.
- Criação e atualização não confirmam a existência do professor, disciplina ou
  turma em suas coleções correspondentes.
- A geração das versões individuais ocorre somente em `/adicionar-questoes` e
  somente para provas objetivas.
- A impressão mantém `alternativa_correta` nos objetos retornados.
- O embaralhamento das alternativas acontece em memória e não é persistido.
- A exclusão da prova-base não remove automaticamente `provas_x_alunos`.
- A rota de impressão não verifica o campo `ativo` da prova-base.
