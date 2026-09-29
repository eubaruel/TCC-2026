# Fluxo de Questões

Documentação completa das rotas responsáveis pelo cadastro, consulta, atualização e exclusão lógica de questões.

## Endereço-base

```text
http://localhost:8080/api/v1/questoes
```

## Resumo das rotas

| Método | Rota | Finalidade |
|---|---|---|
| `POST` | `/api/v1/questoes/` | Cadastrar uma questão |
| `GET` | `/api/v1/questoes/` | Consultar questões |
| `PUT` | `/api/v1/questoes/{_id}` | Atualizar completamente uma questão |
| `DELETE` | `/api/v1/questoes/{_id}` | Desativar uma questão |

## Autenticação

Atualmente, as rotas de questões não exigem token JWT.

---

# Estrutura de uma questão

Uma questão pode ser:

- `Objetiva`;
- `Dissertativa`.

Os campos específicos variam de acordo com o tipo.

## Campos comuns

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `professor` | objeto | Sim | Professor responsável pelo cadastro |
| `professor.nome` | string | Sim | Nome completo do professor |
| `assunto` | string | Sim | Assunto abordado pela questão |
| `disciplina` | lista de strings | Sim | Disciplinas associadas |
| `tipo_questao` | string | Sim | `Objetiva` ou `Dissertativa` |
| `dificuldade` | string | Sim | Nível de dificuldade |
| `autor` | string | Não | Autor ou origem da questão |
| `enunciado` | string | Sim | Texto principal da questão |

## Campos de questão objetiva

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `alternativas` | lista de strings | Sim | Textos das alternativas |
| `alternativa_correta` | string | Sim | Texto da alternativa correta |

## Campos de questão dissertativa

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `numero_linhas` | inteiro | Sim | Quantidade de linhas reservadas para resposta |

---

# Regras de negócio

## Professor

O campo `professor` deve ser um objeto:

```json
{
  "professor": {
    "nome": "Carlos Silva"
  }
}
```

O nome do professor:

- deve ser uma string;
- deve possuir pelo menos 5 caracteres;
- deve conter nome e sobrenome;
- cada parte do nome deve possuir pelo menos 3 caracteres;
- é normalizado para iniciais maiúsculas.

Exemplo de normalização:

```text
Entrada:  "carlos silva"
Saída:    "Carlos Silva"
```

## Assunto

O campo `assunto`:

- deve ser uma string;
- deve possuir pelo menos 2 caracteres;
- não pode conter somente números;
- é normalizado para iniciais maiúsculas.

Exemplo:

```text
Entrada:  "álgebra linear"
Saída:    "Álgebra Linear"
```

## Disciplina

O campo `disciplina`:

- deve ser uma lista;
- cada item deve ser uma string;
- cada item deve possuir pelo menos 2 caracteres;
- cada item deve conter letras;
- os valores são armazenados em letras minúsculas.

Exemplo:

```json
{
  "disciplina": [
    "MAT",
    "Matemática"
  ]
}
```

Após a normalização:

```json
{
  "disciplina": [
    "mat",
    "matemática"
  ]
}
```

## Tipo da questão

São aceitos somente:

```text
Objetiva
Dissertativa
```

O valor não diferencia letras maiúsculas e minúsculas na entrada, pois é normalizado internamente.

Exemplos aceitos:

```text
objetiva
OBJETIVA
Objetiva
```

Todos são convertidos para:

```text
Objetiva
```

## Dificuldade

São aceitos somente:

```text
Muito Fácil
Fácil
Médio
Difícil
Muito Difícil
```

O valor também é normalizado para iniciais maiúsculas.

## Autor

O campo `autor` é opcional.

Quando ele não é enviado, a API utiliza automaticamente o nome do professor.

O autor:

- deve ser uma string;
- deve possuir pelo menos 3 caracteres;
- não pode conter somente números.

## Enunciado

O campo `enunciado`:

- deve ser uma string;
- é obrigatório;
- deve ser único durante o cadastro.

A verificação de duplicidade no cadastro não diferencia letras maiúsculas e minúsculas.

Exemplo: se já existir uma questão com o enunciado:

```text
Quanto vale 2 + 2?
```

O cadastro abaixo também será considerado repetido:

```text
QUANTO VALE 2 + 2?
```

## Alternativas

Questões objetivas devem possuir pelo menos 5 alternativas.

Na entrada da API, as alternativas são enviadas como textos:

```json
{
  "alternativas": [
    "1",
    "2",
    "3",
    "4",
    "5"
  ]
}
```

Cada alternativa:

- deve ser uma string;
- não pode ser vazia;
- tem espaços externos removidos;
- recebe um UUID gerado pela API.

Após o processamento, cada alternativa é armazenada como:

```json
{
  "id": "uuid-gerado-pela-api",
  "texto": "Texto da alternativa"
}
```

## Alternativa correta

No cadastro e na atualização, `alternativa_correta` deve conter o texto de uma das alternativas.

Exemplo de entrada:

```json
{
  "alternativas": [
    "1",
    "2",
    "3",
    "4",
    "5"
  ],
  "alternativa_correta": "4"
}
```

Internamente, a API localiza a alternativa cujo texto é `"4"` e armazena o ID gerado para ela:

```json
{
  "alternativas": [
    {
      "id": "f952af43-3e8e-43bd-9ce5-3225159dc99b",
      "texto": "4"
    }
  ],
  "alternativa_correta": "f952af43-3e8e-43bd-9ce5-3225159dc99b"
}
```

A comparação entre o texto correto e o texto das alternativas diferencia letras maiúsculas e minúsculas.

## Número de linhas

Em questões dissertativas, `numero_linhas`:

- deve ser um número inteiro;
- deve ser maior que zero.

## Campos incompatíveis

Uma questão objetiva:

- deve possuir `alternativas`;
- deve possuir `alternativa_correta`;
- não pode possuir `numero_linhas`.

Uma questão dissertativa:

- deve possuir `numero_linhas`;
- não pode possuir `alternativas`;
- não pode possuir `alternativa_correta`.

---

# Cadastrar questão objetiva

## Rota

```http
POST /api/v1/questoes/
```

## Cabeçalho

```http
Content-Type: application/json
```

## JSON de entrada

```json
{
  "questao": {
    "professor": {
      "nome": "Carlos Silva"
    },
    "assunto": "Álgebra",
    "disciplina": [
      "MAT",
      "Matemática"
    ],
    "tipo_questao": "Objetiva",
    "dificuldade": "Médio",
    "autor": "Carlos Silva",
    "enunciado": "Quanto vale 2 + 2?",
    "alternativas": [
      "1",
      "2",
      "3",
      "4",
      "5"
    ],
    "alternativa_correta": "4"
  }
}
```

O campo `autor` pode ser omitido:

```json
{
  "questao": {
    "professor": {
      "nome": "Carlos Silva"
    },
    "assunto": "Álgebra",
    "disciplina": [
      "MAT",
      "Matemática"
    ],
    "tipo_questao": "Objetiva",
    "dificuldade": "Médio",
    "enunciado": "Quanto vale 2 + 2?",
    "alternativas": [
      "1",
      "2",
      "3",
      "4",
      "5"
    ],
    "alternativa_correta": "4"
  }
}
```

Nesse caso, o autor será definido como:

```text
Carlos Silva
```

## Resposta de sucesso

Código HTTP:

```text
201 Created
```

Resposta:

```json
{
  "sucesso": true,
  "mensagem": "Cadastro realizado com sucesso",
  "data": {
    "questao": {
      "_id": "64b000000000000000000001",
      "professor": {
        "nome": "Carlos Silva"
      },
      "assunto": "Álgebra",
      "disciplina": [
        "mat",
        "matemática"
      ],
      "tipo_questao": "Objetiva",
      "dificuldade": "Médio",
      "autor": "Carlos Silva",
      "enunciado": "Quanto vale 2 + 2?",
      "alternativas": [
        {
          "id": "d9b3cb95-c259-4056-8c7b-70919e7367ee",
          "texto": "1"
        },
        {
          "id": "c906cc17-52bb-441d-8860-b06be3dfd26c",
          "texto": "2"
        },
        {
          "id": "725c71b9-8381-42b4-9e47-f29609f2f0b4",
          "texto": "3"
        },
        {
          "id": "907467fe-9be1-42a3-a8fd-f7795ca879d2",
          "texto": "4"
        },
        {
          "id": "04daf87e-b0d7-4af9-b02a-ff83042dbac0",
          "texto": "5"
        }
      ],
      "alternativa_correta": "907467fe-9be1-42a3-a8fd-f7795ca879d2"
    }
  }
}
```

## Possíveis erros

### Chave `questao` ausente

Código HTTP:

```text
400 Bad Request
```

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'questão' é obrigatório!"
  }
}
```

### Campo obrigatório ausente

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'enunciado' é obrigatório!"
  }
}
```

### Enunciado repetido

```json
{
  "sucesso": false,
  "mensagem": "Enunciado repetido",
  "erro": {
    "mensagem": "A questão de enunciado \"Quanto vale 2 + 2?\" já está cadastrada"
  }
}
```

### Menos de cinco alternativas

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Deve ter pelo menos 5 alternativas"
  }
}
```

### Alternativa correta não encontrada

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Alternativa correta deve estar na lista de alternativas"
  }
}
```

---

# Cadastrar questão dissertativa

## Rota

```http
POST /api/v1/questoes/
```

## JSON de entrada

```json
{
  "questao": {
    "professor": {
      "nome": "Carlos Silva"
    },
    "assunto": "História do Brasil",
    "disciplina": [
      "HIS",
      "História"
    ],
    "tipo_questao": "Dissertativa",
    "dificuldade": "Difícil",
    "autor": "Carlos Silva",
    "enunciado": "Explique as principais causas da Revolução de 1930.",
    "numero_linhas": 8
  }
}
```

Os campos abaixo não devem ser enviados:

```text
alternativas
alternativa_correta
```

## Resposta de sucesso

Código HTTP:

```text
201 Created
```

```json
{
  "sucesso": true,
  "mensagem": "Cadastro realizado com sucesso",
  "data": {
    "questao": {
      "_id": "64b000000000000000000002",
      "professor": {
        "nome": "Carlos Silva"
      },
      "assunto": "História Do Brasil",
      "disciplina": [
        "his",
        "história"
      ],
      "tipo_questao": "Dissertativa",
      "dificuldade": "Difícil",
      "autor": "Carlos Silva",
      "enunciado": "Explique as principais causas da Revolução de 1930.",
      "numero_linhas": 8
    }
  }
}
```

## Possíveis erros

### Número de linhas ausente

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "Questão dissertativa exige número de linhas"
  }
}
```

### Número de linhas inválido

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Número de linhas deve ser maior que zero"
  }
}
```

### Campos de questão objetiva enviados

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "Questão dissertativa não deve possuir alternativas"
  }
}
```

---

# Consultar questões

## Rota

```http
GET /api/v1/questoes/
```

A requisição não possui corpo JSON.

## Consultar todas as questões

```http
GET /api/v1/questoes/
```

## Resposta de sucesso

Código HTTP:

```text
200 OK
```

```json
{
  "sucesso": true,
  "mensagem": "Executado com sucesso",
  "data": {
    "questoes": [
      {
        "_id": "64b000000000000000000001",
        "professor": {
          "nome": "Carlos Silva"
        },
        "assunto": "Álgebra",
        "disciplina": [
          "mat",
          "matemática"
        ],
        "tipo_questao": "Objetiva",
        "dificuldade": "Médio",
        "autor": "Carlos Silva",
        "enunciado": "Quanto vale 2 + 2?",
        "alternativas": [
          {
            "id": "d9b3cb95-c259-4056-8c7b-70919e7367ee",
            "texto": "1"
          },
          {
            "id": "c906cc17-52bb-441d-8860-b06be3dfd26c",
            "texto": "2"
          },
          {
            "id": "725c71b9-8381-42b4-9e47-f29609f2f0b4",
            "texto": "3"
          },
          {
            "id": "907467fe-9be1-42a3-a8fd-f7795ca879d2",
            "texto": "4"
          },
          {
            "id": "04daf87e-b0d7-4af9-b02a-ff83042dbac0",
            "texto": "5"
          }
        ],
        "alternativa_correta": "907467fe-9be1-42a3-a8fd-f7795ca879d2"
      }
    ]
  }
}
```

O campo interno `ativo` não é retornado.

A consulta retorna somente questões ativas.

## Consulta sem resultados

Uma consulta sem resultados não retorna `404`.

Ela retorna HTTP `200` com uma lista vazia:

```json
{
  "sucesso": true,
  "mensagem": "Executado com sucesso",
  "data": {
    "questoes": []
  }
}
```

---

# Filtros de consulta

Os filtros são enviados por query parameters.

## Filtros permitidos

| Parâmetro | Campo pesquisado | Comportamento |
|---|---|---|
| `id` | `_id` | Correspondência exata |
| `nome` | `professor.nome` | Correspondência exata |
| `assunto` | `assunto` | Correspondência exata |
| `disciplina` | `disciplina` | Busca valor exato dentro da lista |
| `tipo_questao` | `tipo_questao` | Correspondência exata |
| `dificuldade` | `dificuldade` | Correspondência exata |
| `autor` | `autor` | Correspondência exata |
| `enunciado` | `enunciado` | Busca parcial sem diferenciar maiúsculas e minúsculas |

É possível combinar filtros.

## Consultar por ID

```http
GET /api/v1/questoes/?id=64b000000000000000000001
```

Um ID MongoDB inválido produz uma lista vazia com HTTP `200`.

## Consultar por professor

```http
GET /api/v1/questoes/?nome=Carlos%20Silva
```

## Consultar por assunto

```http
GET /api/v1/questoes/?assunto=Álgebra
```

## Consultar por disciplina

Como as disciplinas são armazenadas em letras minúsculas, utilize:

```http
GET /api/v1/questoes/?disciplina=matemática
```

## Consultar por tipo

```http
GET /api/v1/questoes/?tipo_questao=Objetiva
```

## Consultar por dificuldade

```http
GET /api/v1/questoes/?dificuldade=Médio
```

## Consultar por autor

```http
GET /api/v1/questoes/?autor=Carlos%20Silva
```

## Consultar por parte do enunciado

```http
GET /api/v1/questoes/?enunciado=quanto%20vale
```

Essa pesquisa:

- aceita parte do enunciado;
- não diferencia letras maiúsculas e minúsculas;
- trata caracteres especiais como texto literal.

## Combinar filtros

```http
GET /api/v1/questoes/?disciplina=matemática&tipo_questao=Objetiva&dificuldade=Médio
```

## Parâmetro desconhecido

Exemplo inválido:

```http
GET /api/v1/questoes/?senha=123
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Parâmetro não permitido: senha",
  "erro": null
}
```

Código HTTP:

```text
400 Bad Request
```

---

# Atualizar questão objetiva

## Rota

```http
PUT /api/v1/questoes/{_id}
```

Exemplo:

```http
PUT /api/v1/questoes/64b000000000000000000001
```

A atualização é completa. Portanto, todos os campos obrigatórios devem ser enviados novamente.

## JSON de entrada

```json
{
  "questao": {
    "professor": {
      "nome": "Carlos Silva"
    },
    "assunto": "Aritmética",
    "disciplina": [
      "MAT",
      "Matemática"
    ],
    "tipo_questao": "Objetiva",
    "dificuldade": "Fácil",
    "autor": "Carlos Silva",
    "enunciado": "Quanto vale 10 + 10?",
    "alternativas": [
      "10",
      "15",
      "20",
      "25",
      "30"
    ],
    "alternativa_correta": "20"
  }
}
```

## Comportamento das alternativas na atualização

As alternativas continuam sendo enviadas como textos.

Ao atualizar:

- novas instâncias de alternativas são criadas;
- novos UUIDs são gerados;
- os IDs anteriores das alternativas são substituídos;
- `alternativa_correta` passa a guardar o novo ID correspondente.

## Resposta de sucesso

Código HTTP:

```text
200 OK
```

```json
{
  "sucesso": true,
  "mensagem": "Atualizado com sucesso",
  "data": {
    "questao": {
      "_id": "64b000000000000000000001",
      "professor": {
        "nome": "Carlos Silva"
      },
      "assunto": "Aritmética",
      "disciplina": [
        "mat",
        "matemática"
      ],
      "tipo_questao": "Objetiva",
      "dificuldade": "Fácil",
      "autor": "Carlos Silva",
      "enunciado": "Quanto vale 10 + 10?",
      "alternativas": [
        {
          "id": "novo-uuid-1",
          "texto": "10"
        },
        {
          "id": "novo-uuid-2",
          "texto": "15"
        },
        {
          "id": "novo-uuid-3",
          "texto": "20"
        },
        {
          "id": "novo-uuid-4",
          "texto": "25"
        },
        {
          "id": "novo-uuid-5",
          "texto": "30"
        }
      ],
      "alternativa_correta": "novo-uuid-3"
    }
  }
}
```

## Questão inexistente ou inativa

Código HTTP:

```text
400 Bad Request
```

```json
{
  "sucesso": false,
  "mensagem": "Questão não existe",
  "erro": {
    "mensagem": "A questão com Id fornecido não existe no banco de dados"
  }
}
```

Um `_id` em formato MongoDB inválido também resulta nesse erro.

---

# Atualizar questão dissertativa

## Rota

```http
PUT /api/v1/questoes/{_id}
```

## JSON de entrada

```json
{
  "questao": {
    "professor": {
      "nome": "Carlos Silva"
    },
    "assunto": "História do Brasil",
    "disciplina": [
      "HIS",
      "História"
    ],
    "tipo_questao": "Dissertativa",
    "dificuldade": "Médio",
    "autor": "Carlos Silva",
    "enunciado": "Explique as consequências da Revolução de 1930.",
    "numero_linhas": 10
  }
}
```

## Resposta de sucesso

```json
{
  "sucesso": true,
  "mensagem": "Atualizado com sucesso",
  "data": {
    "questao": {
      "_id": "64b000000000000000000002",
      "professor": {
        "nome": "Carlos Silva"
      },
      "assunto": "História Do Brasil",
      "disciplina": [
        "his",
        "história"
      ],
      "tipo_questao": "Dissertativa",
      "dificuldade": "Médio",
      "autor": "Carlos Silva",
      "enunciado": "Explique as consequências da Revolução de 1930.",
      "numero_linhas": 10
    }
  }
}
```

---

# Excluir questão

## Rota

```http
DELETE /api/v1/questoes/{_id}
```

Exemplo:

```http
DELETE /api/v1/questoes/64b000000000000000000001
```

A requisição não possui corpo JSON.

## Exclusão lógica

A questão não é removida fisicamente do MongoDB.

O documento é atualizado internamente para:

```json
{
  "ativo": false
}
```

Depois da exclusão:

- a questão deixa de aparecer nas consultas;
- a questão não pode ser selecionada para novas provas;
- os demais dados permanecem armazenados.

## Resposta de sucesso

Código HTTP:

```text
200 OK
```

```json
{
  "sucesso": true,
  "mensagem": "Excluído com sucesso",
  "data": null
}
```

## Questão inexistente, inativa ou ID inválido

Código HTTP:

```text
404 Not Found
```

```json
{
  "sucesso": false,
  "mensagem": "Não existe questão com o id 64b000000000000000000001",
  "erro": null
}
```

---

# Formato geral dos erros de validação

Erros gerados pelos modelos, como tipos incorretos ou valores inválidos, retornam:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Descrição da validação que falhou"
  }
}
```

Código HTTP:

```text
400 Bad Request
```

## Erro interno

Erros inesperados retornam:

```json
{
  "sucesso": false,
  "mensagem": "Ocorreu um erro interno no servidor",
  "erro": {
    "codigo": "INTERNAL_ERROR"
  }
}
```

Código HTTP:

```text
500 Internal Server Error
```

---

# Fluxo recomendado de utilização

1. Cadastre uma questão com `POST /api/v1/questoes/`.
2. Consulte as questões com `GET /api/v1/questoes/`.
3. Utilize filtros para localizar questões específicas.
4. Armazene o `_id` das questões selecionadas no frontend.
5. Envie somente esses IDs no vetor `questoes` ao cadastrar uma prova.
6. Atualize uma questão com `PUT /api/v1/questoes/{_id}` quando necessário.
7. Desative uma questão com `DELETE /api/v1/questoes/{_id}`.

## Exemplo de seleção para uma prova

A consulta de questões retorna:

```json
{
  "_id": "64b000000000000000000001",
  "enunciado": "Quanto vale 2 + 2?"
}
```

O frontend deve utilizar somente o `_id` ao montar o JSON da prova:

```json
{
  "questoes": [
    "64b000000000000000000001",
    "64b000000000000000000002",
    "64b000000000000000000003",
    "64b000000000000000000004",
    "64b000000000000000000005"
  ]
}
```