# Fluxo de provas

Documentação das rotas responsáveis pela criação da prova-base, seleção das
questões, geração das versões individuais, montagem para impressão, consulta,
atualização e exclusão lógica.

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
| `PATCH` | `/api/v1/provas/{_id}/adicionar-questoes` | Definir as questões e gerar as versões dos alunos |
| `GET` | `/api/v1/provas/imprimir-provas/{_id}` | Montar as versões completas para impressão |
| `GET` | `/api/v1/provas/` | Consultar provas ativas |
| `PUT` | `/api/v1/provas/{_id}` | Substituir os dados de uma prova ativa |
| `DELETE` | `/api/v1/provas/{_id}` | Desativar uma prova |

---

# Visão geral do fluxo

1. O processo pedagógico cria uma prova-base por `/criar-prova`.
2. A prova é armazenada com `questoes: []` e status
   `Aguardando questões`.
3. O professor envia os IDs escolhidos para `/adicionar-questoes`.
4. A API valida e salva esses IDs na prova-base.
5. Se a prova for objetiva, a API cria uma configuração individual na coleção
   `provas_x_alunos` para cada aluno ativo das turmas vinculadas.
6. `/imprimir-provas/{_id}` usa essas configurações para retornar as questões
   completas na ordem de cada aluno e com as alternativas posicionadas.

As provas dissertativas podem receber questões, mas não geram documentos em
`provas_x_alunos` no fluxo atual.

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
  "status": "Aguardando questões",
  "tipo": "Objetiva",
  "serie": 3,
  "bimestre": "1° bimestre",
  "data_de_aplicacao": "2026-08-20",
  "questoes": [
    "66c49f5a2ce79c0f588b1601",
    "66c49f5a2ce79c0f588b1602"
  ],
  "ativo": true
}
```

O campo `ativo` existe no banco, mas é omitido nas respostas de consulta.

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

Na rota `PUT`, o registro não é obrigatório pelo middleware atual. Se omitido,
o documento atualizado preserva somente o nome do professor.

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
Dissertativa
```

O valor é normalizado com espaços externos removidos e iniciais maiúsculas.
Todas as questões selecionadas devem possuir o mesmo tipo da prova.

Somente provas objetivas geram documentos em `provas_x_alunos`.

## Status

O status é uma string sem lista fixa de valores.

Na criação, não deve ser enviado. A API define automaticamente:

```text
Aguardando questões
```

`/adicionar-questoes` não altera o status. Na atualização completa por `PUT`, o
status deve ser enviado e substitui o valor atual.

## Série

Deve ser um número inteiro maior que zero.

## Bimestre

Deve ser uma string. Os espaços externos são removidos, mas não existe uma
lista fixa de bimestres permitidos.

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
`/adicionar-questoes`, deve conter ao menos um ID.

Regras aplicadas na adição e no `PUT`:

- a estrutura deve ser uma lista;
- deve haver ao menos uma questão;
- cada ID deve ser uma string não vazia;
- espaços externos são removidos;
- IDs repetidos são rejeitados;
- todas as questões devem existir e estar ativas;
- o tipo da questão deve ser igual ao tipo da prova;
- a questão deve possuir o código ou o nome da disciplina da prova.

A comparação da disciplina ignora maiúsculas, minúsculas e espaços externos.

Exemplo válido com uma questão:

```json
{
  "questoes": [
    "66c49f5a2ce79c0f588b1601"
  ]
}
```

Não existe quantidade mínima de cinco questões. Qualquer quantidade a partir de
uma é aceita.

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
    "bimestre": "1° bimestre",
    "data_de_aplicacao": "2026-08-20"
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
      "bimestre": "1° bimestre",
      "data_de_aplicacao": "2026-08-20",
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

A operação substitui o vetor atual da prova-base. Ela não acrescenta itens ao
vetor existente.

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

Cada repetição gera novamente:

- a ordem das questões;
- a posição da alternativa correta de cada questão.

Versões de alunos que não pertencem mais às turmas são removidas. Se nenhuma
matrícula ativa for encontrada, todas as versões individuais daquela prova são
removidas e `provas_alunos_geradas` retorna `0`.

Documentos pertencentes a outras provas não são alterados.

## Resposta de sucesso

Código: `200 OK`.

```json
{
  "sucesso": true,
  "mensagem": "Questões adicionadas com sucesso",
  "data": {
    "prova": {
      "_id": "66c4a6c22ce79c0f588b1621",
      "questoes": [
        "66c49f5a2ce79c0f588b1601",
        "66c49f5a2ce79c0f588b1602"
      ]
    },
    "provas_alunos_geradas": 32
  }
}
```

O status da prova não é alterado.

Para uma prova dissertativa, a resposta também contém
`provas_alunos_geradas`, mas seu valor é `0`.

## Erros principais

| Situação | Código | Mensagem principal |
|---|---:|---|
| Prova inexistente, inativa ou ID inválido | `404` | `Prova não encontrada` |
| Lista vazia | `400` | `Número de questões insuficiente` |
| `questoes` não é lista | `400` | `Questões inválidas` |
| ID não é string ou está vazio | `400` | `Id de questão inválido` |
| IDs repetidos | `400` | `Questões repetidas` |
| Questão inexistente ou inativa | `400` | `Questão não encontrada` |
| Tipo incompatível | `400` | `Tipo de questão incompatível` |
| Disciplina incompatível | `400` | `Disciplina incompatível` |

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

# Imprimir provas

## Rota

```http
GET /api/v1/provas/imprimir-provas/{_id}
```

A rota não recebe corpo JSON e não altera documentos no banco.

Ela consulta diretamente `provas_x_alunos`; não confirma novamente se a
prova-base existe ou continua ativa. Por isso, versões que permanecerem nessa
coleção após a exclusão lógica da prova ainda podem ser retornadas.

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

As alternativas incorretas são embaralhadas novamente em cada chamada. A ordem
das questões e a posição da correta permanecem definidas pelo documento do
aluno.

O campo `alternativa_correta` continua presente no objeto completo retornado.

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
        "matricula_aluno": 50280715,
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

Um ID sem documentos associados, inclusive um valor fora do formato de
`ObjectId`, retorna `200 OK`:

```json
{
  "sucesso": true,
  "mensagem": "Provas montadas com sucesso",
  "data": {
    "id_prova": "id-sem-versoes",
    "provas_alunos": []
  }
}
```

## Erros principais

| Situação | Código | Mensagem principal |
|---|---:|---|
| Questão referenciada inexistente ou inativa | `404` | `Questão não encontrada` |
| Questão objetiva sem alternativas válidas | `400` | `Questão inválida` |
| ID da alternativa correta não localizado | `400` | `Questão inválida` |
| Posição não inteira ou fora do vetor | `400` | `Posição da alternativa correta inválida` |

Se uma questão estiver ausente, a rota interrompe toda a montagem para não
entregar provas incompletas.

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
        "status": "Aguardando questões",
        "tipo": "Objetiva",
        "serie": 3,
        "bimestre": "1° bimestre",
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
| `status` | string | `status` |
| `tipo` | string | `tipo` |
| `serie` | inteiro | `serie` |
| `bimestre` | string | `bimestre` |
| `data_de_aplicacao` | string | `data_de_aplicacao` |

Exemplos:

```http
GET /api/v1/provas/?id=66c4a6c22ce79c0f588b1621
GET /api/v1/provas/?id_turma=Turma%202026%20A
GET /api/v1/provas/?codigo_disciplina=MAT&tipo=Objetiva&serie=3
```

Os filtros são combinados com condição lógica `E` e usam correspondência exata.
No MongoDB, consultar uma string em `id_turma` também encontra documentos em que
o campo é uma lista contendo essa string.

Parâmetros vazios são ignorados. Um parâmetro desconhecido retorna `400`. Um ID
com formato inválido retorna uma lista vazia. Um valor não inteiro em `serie`
também retorna `400`.

---

# Atualizar prova

## Rota

```http
PUT /api/v1/provas/{_id}
```

A atualização não é parcial. O corpo deve apresentar novamente os dados da
prova, incluindo status e questões.

```json
{
  "prova": {
    "id_turma": "Turma 2026 B",
    "professor": {
      "registro": 101,
      "nome": "Carlos Silva"
    },
    "disciplina": {
      "codigo_disciplina": "MAT",
      "nome_disciplina": "Matemática"
    },
    "status": "Pronta para aplicação",
    "tipo": "Objetiva",
    "serie": 3,
    "bimestre": "1° bimestre",
    "data_de_aplicacao": "2026-08-22",
    "questoes": [
      "66c49f5a2ce79c0f588b1601",
      "66c49f5a2ce79c0f588b1602"
    ]
  }
}
```

O service substitui:

- `id_turma`;
- `professor`;
- `disciplina`;
- `status`;
- `tipo`;
- `serie`;
- `bimestre`;
- `data_de_aplicacao`;
- `questoes`.

`_id` e `ativo` são preservados.

As questões passam pelas mesmas validações de existência, atividade, tipo,
disciplina e repetição usadas em `/adicionar-questoes`.

Importante: a rota `PUT` atualiza a prova-base, mas não recria nem sincroniza os
documentos em `provas_x_alunos`. Para refazer as versões individuais de uma
prova objetiva, utilize `/adicionar-questoes` depois da atualização.

## Resposta de sucesso

Código: `200 OK`.

```json
{
  "sucesso": true,
  "mensagem": "Atualizado com sucesso",
  "data": {
    "prova": {
      "_id": "66c4a6c22ce79c0f588b1621",
      "id_turma": "Turma 2026 B",
      "professor": {
        "nome": "Carlos Silva"
      },
      "disciplina": {
        "codigo_disciplina": "MAT",
        "nome_disciplina": "Matemática"
      },
      "status": "Pronta para aplicação",
      "tipo": "Objetiva",
      "serie": 3,
      "bimestre": "1° bimestre",
      "data_de_aplicacao": "2026-08-22",
      "questoes": [
        "66c49f5a2ce79c0f588b1601",
        "66c49f5a2ce79c0f588b1602"
      ]
    }
  }
}
```

A resposta do controle atual retorna o professor apenas com `nome`, embora o
registro possa ter sido persistido se enviado. Para consultar o documento
persistido, use `GET /api/v1/provas/?id={_id}`.

## Erros principais

- prova inexistente ou ID inválido: `400`, mensagem `Prova não existe`;
- prova inativa: `400`, mensagem `Não foi possível atualizar a prova`;
- corpo incompleto ou valores inválidos: `400` quando a falha é tratada pelos
  modelos;
- questão inválida: utiliza as mesmas mensagens da seleção de questões.

O middleware atual do `PUT` não valida previamente a estrutura completa do
corpo. O cliente deve seguir exatamente o formato documentado.

---

# Excluir prova

## Rota

```http
DELETE /api/v1/provas/{_id}
```

A exclusão é lógica. A API altera:

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
  "mensagem": "Não existe prova com o id 66c4a6c22ce79c0f588b1621",
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
