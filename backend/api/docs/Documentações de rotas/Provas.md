# Fluxo de Provas

Documentação completa das rotas responsáveis pelo cadastro, consulta, atualização e exclusão lógica de provas.

## Endereço-base

```text
http://localhost:8080/api/v1/provas
```

## Resumo das rotas

| Método | Rota | Finalidade |
|---|---|---|
| `POST` | `/api/v1/provas/` | Cadastrar uma prova |
| `GET` | `/api/v1/provas/` | Consultar provas |
| `PUT` | `/api/v1/provas/{_id}` | Atualizar uma prova |
| `DELETE` | `/api/v1/provas/{_id}` | Desativar uma prova |

## Autenticação

Atualmente, as rotas de provas não exigem token JWT.

---

# Estrutura de uma prova

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `_id` | string | Gerado pela API | Identificador da prova no MongoDB |
| `id_turma` | string ou lista de strings | Sim | Turma ou turmas que realizarão a prova |
| `professor` | objeto | Sim | Professor responsável pela prova |
| `professor.nome` | string | Sim | Nome completo do professor |
| `disciplina` | objeto | Sim | Disciplina da prova |
| `disciplina.codigo_disciplina` | string | Sim | Código da disciplina |
| `disciplina.nome_disciplina` | string | Sim | Nome da disciplina |
| `status` | string | Sim | Estado de correção da prova |
| `tipo` | string | Sim | Tipo das questões da prova |
| `serie` | inteiro | Sim | Série para a qual a prova será aplicada |
| `bimestre` | string | Sim | Bimestre correspondente |
| `data_de_aplicacao` | string | Sim | Data prevista para aplicação |
| `questoes` | lista de strings | Sim | IDs das questões selecionadas |
| `ativo` | booleano | Gerenciado pela API | Indica se a prova está ativa |

Exemplo:

```json
{
  "_id": "66c4a6c22ce79c0f588b1621",
  "id_turma": "Turma 2026 A",
  "professor": {
    "nome": "Carlos Silva"
  },
  "disciplina": {
    "codigo_disciplina": "MAT",
    "nome_disciplina": "Matemática"
  },
  "status": "Não Corrigida",
  "tipo": "Objetiva",
  "serie": 3,
  "bimestre": "1° bimestre",
  "data_de_aplicacao": "2026-08-20",
  "questoes": [
    "66c49f5a2ce79c0f588b1601",
    "66c49f5a2ce79c0f588b1602",
    "66c49f5a2ce79c0f588b1603",
    "66c49f5a2ce79c0f588b1604",
    "66c49f5a2ce79c0f588b1605"
  ]
}
```

---

# Regra principal das questões

A prova recebe, armazena e retorna somente os IDs das questões.

O campo `questoes` não deve conter os objetos completos das questões.

Formato correto:

```json
{
  "questoes": [
    "66c49f5a2ce79c0f588b1601",
    "66c49f5a2ce79c0f588b1602",
    "66c49f5a2ce79c0f588b1603",
    "66c49f5a2ce79c0f588b1604",
    "66c49f5a2ce79c0f588b1605"
  ]
}
```

Formato incorreto:

```json
{
  "questoes": [
    {
      "_id": "66c49f5a2ce79c0f588b1601",
      "enunciado": "Quanto é 2 + 2?",
      "tipo_questao": "Objetiva"
    }
  ]
}
```

Caso o frontend precise exibir o conteúdo completo das questões de uma prova, deve:

1. consultar a prova;
2. obter o vetor `questoes`;
3. consultar o fluxo de questões utilizando os IDs retornados.

---

# Regras de negócio

## Identificador da prova

O campo `_id`:

- é gerado automaticamente pelo MongoDB;
- é convertido para string nas respostas da API;
- não deve ser enviado no cadastro;
- identifica a prova nas rotas de atualização e exclusão;
- normalmente possui 24 caracteres hexadecimais.

Exemplo:

```text
66c4a6c22ce79c0f588b1621
```

## Turma

O campo `id_turma` pode ser enviado como uma string:

```json
{
  "id_turma": "Turma 2026 A"
}
```

Também pode ser enviado como uma lista de strings:

```json
{
  "id_turma": [
    "Turma 2026 A",
    "Turma 2026 B"
  ]
}
```

Cada turma:

- deve ser uma string;
- deve possuir pelo menos 10 caracteres;
- tem os espaços externos removidos.

Exemplo inválido:

```json
{
  "id_turma": "3A"
}
```

Atualmente:

- a API não verifica se a turma informada existe;
- a API não impede turmas repetidas;
- uma lista vazia de turmas não é rejeitada pelo modelo atual.

## Professor

O campo `professor` deve conter:

```json
{
  "nome": "Carlos Silva"
}
```

O nome do professor:

- deve ser uma string;
- deve possuir pelo menos 5 caracteres;
- deve conter nome e sobrenome;
- cada parte do nome deve possuir pelo menos 3 caracteres;
- tem os espaços externos removidos;
- é armazenado com as iniciais em letras maiúsculas.

Exemplo:

```text
Entrada:    "carlos silva"
Armazenado: "Carlos Silva"
```

Atualmente, a API não consulta o fluxo de usuários para verificar se o professor informado está cadastrado ou ativo.

## Disciplina

O campo `disciplina` deve possuir:

```json
{
  "codigo_disciplina": "MAT",
  "nome_disciplina": "Matemática"
}
```

### Código da disciplina

O campo `codigo_disciplina`:

- deve ser uma string;
- não pode ser nulo;
- tem os espaços externos removidos.

### Nome da disciplina

O campo `nome_disciplina`:

- deve ser uma string;
- deve possuir pelo menos 3 caracteres;
- tem os espaços externos removidos;
- é armazenado com as iniciais em letras maiúsculas.

Atualmente, o cadastro da prova não verifica se a disciplina existe no fluxo de disciplinas.

Entretanto, a disciplina informada é utilizada para verificar a compatibilidade das questões selecionadas.

## Status

O campo `status` aceita somente:

```text
Corrigida
Não Corrigida
```

Exemplo:

```json
{
  "status": "Não Corrigida"
}
```

A comparação é sensível a letras maiúsculas e minúsculas.

Portanto, o seguinte valor é inválido:

```json
{
  "status": "não corrigida"
}
```

A API remove os espaços externos, mas não altera a capitalização do status.

## Tipo da prova

O campo `tipo` aceita somente:

```text
Objetiva
Dissertativa
```

Exemplos:

```json
{
  "tipo": "Objetiva"
}
```

```json
{
  "tipo": "Dissertativa"
}
```

O valor tem os espaços externos removidos e é normalizado com a primeira letra maiúscula.

Por exemplo:

```text
Entrada:    "objetiva"
Armazenado: "Objetiva"
```

Todas as questões selecionadas devem possuir o mesmo tipo da prova.

Uma prova objetiva aceita somente questões objetivas.

Uma prova dissertativa aceita somente questões dissertativas.

## Série

O campo `serie`:

- deve ser um número inteiro;
- deve ser maior que zero.

Exemplo válido:

```json
{
  "serie": 3
}
```

Exemplos inválidos:

```json
{
  "serie": "3"
}
```

```json
{
  "serie": 0
}
```

## Bimestre

O campo `bimestre`:

- deve ser uma string;
- não pode ser nulo;
- tem os espaços externos removidos.

Exemplo:

```json
{
  "bimestre": "1° bimestre"
}
```

Atualmente, a API não limita o bimestre a uma lista de valores específicos.

## Data de aplicação

O campo `data_de_aplicacao`:

- deve ser uma string;
- não pode ser nulo;
- tem os espaços externos removidos.

Formato recomendado:

```text
AAAA-MM-DD
```

Exemplo:

```json
{
  "data_de_aplicacao": "2026-08-20"
}
```

Atualmente, a API não valida:

- se a string segue o formato `AAAA-MM-DD`;
- se a data existe no calendário;
- se a data está no passado ou no futuro.

Portanto, o frontend deve enviar a data no formato padronizado.

## Questões

O campo `questoes`:

- deve ser uma lista;
- deve possuir pelo menos 5 IDs;
- deve conter somente strings;
- não pode conter IDs vazios;
- não pode conter IDs repetidos;
- deve referenciar questões existentes;
- deve referenciar somente questões ativas;
- deve conter questões do mesmo tipo da prova;
- deve conter questões compatíveis com a disciplina da prova.

Exemplo válido:

```json
{
  "questoes": [
    "66c49f5a2ce79c0f588b1601",
    "66c49f5a2ce79c0f588b1602",
    "66c49f5a2ce79c0f588b1603",
    "66c49f5a2ce79c0f588b1604",
    "66c49f5a2ce79c0f588b1605"
  ]
}
```

Os espaços externos dos IDs são removidos antes do armazenamento.

A ordem dos IDs recebidos é preservada no documento da prova.

### Quantidade mínima

A prova deve possuir pelo menos cinco questões.

Exemplo inválido:

```json
{
  "questoes": [
    "66c49f5a2ce79c0f588b1601",
    "66c49f5a2ce79c0f588b1602"
  ]
}
```

### IDs como strings

Cada questão deve ser representada por uma string.

Exemplo inválido:

```json
{
  "questoes": [
    123,
    456,
    789,
    101,
    112
  ]
}
```

### IDs vazios

Não são aceitos IDs vazios ou formados somente por espaços.

Exemplo inválido:

```json
{
  "questoes": [
    "66c49f5a2ce79c0f588b1601",
    "66c49f5a2ce79c0f588b1602",
    "66c49f5a2ce79c0f588b1603",
    "66c49f5a2ce79c0f588b1604",
    "   "
  ]
}
```

### IDs repetidos

A mesma questão não pode aparecer mais de uma vez na prova.

Exemplo inválido:

```json
{
  "questoes": [
    "66c49f5a2ce79c0f588b1601",
    "66c49f5a2ce79c0f588b1601",
    "66c49f5a2ce79c0f588b1601",
    "66c49f5a2ce79c0f588b1601",
    "66c49f5a2ce79c0f588b1601"
  ]
}
```

### Existência das questões

Todos os IDs devem pertencer a questões existentes e ativas.

A requisição é rejeitada quando:

- o ID não possui um formato aceito pelo MongoDB;
- o ID não existe;
- a questão foi excluída logicamente;
- uma ou mais questões não foram localizadas.

### Compatibilidade de tipo

O campo `tipo_questao` de cada questão deve corresponder ao campo `tipo` da prova.

Exemplo:

```text
Tipo da prova: Objetiva
Tipo exigido das questões: Objetiva
```

Uma questão dissertativa não pode ser inserida em uma prova objetiva.

### Compatibilidade de disciplina

Cada questão possui uma lista de disciplinas associadas.

Para ser aceita, a questão deve conter pelo menos uma referência correspondente:

- ao código da disciplina da prova; ou
- ao nome da disciplina da prova.

Exemplo de disciplina da prova:

```json
{
  "codigo_disciplina": "MAT",
  "nome_disciplina": "Matemática"
}
```

A questão pode possuir:

```json
{
  "disciplina": [
    "MAT",
    "Matemática"
  ]
}
```

A comparação ignora:

- diferenças entre letras maiúsculas e minúsculas;
- espaços externos.

Assim, os seguintes valores são considerados compatíveis:

```text
MAT
mat
Mat
```

## Estado ativo

A prova é cadastrada automaticamente com:

```json
{
  "ativo": true
}
```

O campo não deve ser enviado pelo frontend.

A exclusão é lógica e altera o estado para:

```json
{
  "ativo": false
}
```

Provas inativas não aparecem nas consultas e não podem ser atualizadas.

---

# Cadastrar prova

## Rota

```http
POST /api/v1/provas/
```

## Cabeçalho

```http
Content-Type: application/json
```

## JSON de entrada

```json
{
  "prova": {
    "id_turma": "Turma 2026 A",
    "professor": {
      "nome": "Carlos Silva"
    },
    "disciplina": {
      "codigo_disciplina": "MAT",
      "nome_disciplina": "Matemática"
    },
    "status": "Não Corrigida",
    "tipo": "Objetiva",
    "serie": 3,
    "bimestre": "1° bimestre",
    "data_de_aplicacao": "2026-08-20",
    "questoes": [
      "66c49f5a2ce79c0f588b1601",
      "66c49f5a2ce79c0f588b1602",
      "66c49f5a2ce79c0f588b1603",
      "66c49f5a2ce79c0f588b1604",
      "66c49f5a2ce79c0f588b1605"
    ]
  }
}
```

Todos os campos apresentados são obrigatórios.

O campo `_id` não deve ser enviado. Ele é gerado automaticamente pelo banco.

O campo `ativo` também não deve ser enviado. A API atribui automaticamente o valor `true`.

## Exemplo com várias turmas

```json
{
  "prova": {
    "id_turma": [
      "Turma 2026 A",
      "Turma 2026 B"
    ],
    "professor": {
      "nome": "Carlos Silva"
    },
    "disciplina": {
      "codigo_disciplina": "MAT",
      "nome_disciplina": "Matemática"
    },
    "status": "Não Corrigida",
    "tipo": "Objetiva",
    "serie": 3,
    "bimestre": "1° bimestre",
    "data_de_aplicacao": "2026-08-20",
    "questoes": [
      "66c49f5a2ce79c0f588b1601",
      "66c49f5a2ce79c0f588b1602",
      "66c49f5a2ce79c0f588b1603",
      "66c49f5a2ce79c0f588b1604",
      "66c49f5a2ce79c0f588b1605"
    ]
  }
}
```

## Resposta de sucesso

Código HTTP:

```http
201 Created
```

Resposta:

```json
{
  "sucesso": true,
  "mensagem": "Cadastro realizado com sucesso",
  "data": {
    "prova": {
      "_id": "66c4a6c22ce79c0f588b1621",
      "id_turma": "Turma 2026 A",
      "professor": {
        "nome": "Carlos Silva"
      },
      "disciplina": {
        "codigo_disciplina": "MAT",
        "nome_disciplina": "Matemática"
      },
      "status": "Não Corrigida",
      "tipo": "Objetiva",
      "serie": 3,
      "bimestre": "1° bimestre",
      "data_de_aplicacao": "2026-08-20",
      "questoes": [
        "66c49f5a2ce79c0f588b1601",
        "66c49f5a2ce79c0f588b1602",
        "66c49f5a2ce79c0f588b1603",
        "66c49f5a2ce79c0f588b1604",
        "66c49f5a2ce79c0f588b1605"
      ]
    }
  }
}
```

A resposta do cadastro é construída a partir do JSON recebido.

Por isso, ela pode não exibir algumas normalizações realizadas antes do armazenamento, como:

- remoção de espaços dos IDs das questões;
- capitalização do tipo;
- capitalização do nome do professor;
- capitalização do nome da disciplina.

Para obter a representação armazenada, realize posteriormente uma consulta `GET`.

## Possíveis erros

### Chave `prova` ausente

Código HTTP:

```http
400 Bad Request
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'prova' é obrigatório!"
  }
}
```

### Campo obrigatório ausente

Exemplo sem `status`:

```json
{
  "prova": {
    "id_turma": "Turma 2026 A",
    "professor": {
      "nome": "Carlos Silva"
    },
    "disciplina": {
      "codigo_disciplina": "MAT",
      "nome_disciplina": "Matemática"
    },
    "tipo": "Objetiva",
    "serie": 3,
    "bimestre": "1° bimestre",
    "data_de_aplicacao": "2026-08-20",
    "questoes": []
  }
}
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'status' é obrigatório!"
  }
}
```

### Nome do professor ausente

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'nome' do professor é obrigatório!"
  }
}
```

### Campo da disciplina ausente

Exemplo sem `codigo_disciplina`.

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'codigo_disciplina' da disciplina é obrigatório!"
  }
}
```

### Quantidade insuficiente de questões

Código HTTP:

```http
400 Bad Request
```

Resposta possível:

```json
{
  "sucesso": false,
  "mensagem": "Número de questões insuficiente",
  "erro": {
    "mensagem": "A prova deve possuir ao menos cinco questões"
  }
}
```

Dependendo da quantidade de IDs e da etapa da validação atingida, a resposta também pode seguir o formato geral de erro do modelo:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "A prova deve possuir ao menos cinco questões"
  }
}
```

Em ambos os casos, a regra é a mesma: são necessárias pelo menos cinco questões.

### Campo `questoes` não é uma lista

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Questões inválidas",
  "erro": {
    "mensagem": "O campo 'questoes' deve ser uma lista de ids"
  }
}
```

### ID da questão não é string

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Id de questão inválido",
  "erro": {
    "mensagem": "O id da questão 3 deve ser uma string"
  }
}
```

A numeração começa em `1` e indica a posição do ID inválido no vetor.

### ID vazio

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Id de questão inválido",
  "erro": {
    "mensagem": "O id da questão 5 não pode ser vazio"
  }
}
```

### Questões repetidas

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Questões repetidas",
  "erro": {
    "mensagem": "A prova não pode conter ids de questões repetidos"
  }
}
```

### Questão inexistente ou inativa

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Questão não encontrada",
  "erro": {
    "mensagem": "Uma ou mais questões não existem ou estão inativas"
  }
}
```

Por segurança lógica, a API não informa nessa resposta qual dos IDs não foi encontrado.

### Tipo incompatível

Exemplo: prova objetiva contendo uma questão dissertativa.

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Tipo de questão incompatível",
  "erro": {
    "mensagem": "A questão 2 não é do tipo Objetiva"
  }
}
```

O número apresentado indica a posição da questão no vetor recebido.

### Disciplina incompatível

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Disciplina incompatível",
  "erro": {
    "mensagem": "A questão 4 não pertence à disciplina da prova"
  }
}
```

### Status inválido

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Status inválido"
  }
}
```

### Tipo inválido

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Tipo inválido"
  }
}
```

### Série inválida

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Série deve ser maior que zero"
  }
}
```

### Turma inválida

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Turma deve ter ao menos 10 caracteres"
  }
}
```

---

# Consultar provas

## Rota

```http
GET /api/v1/provas/
```

A rota não exige corpo JSON.

## Consultar todas as provas

```http
GET /api/v1/provas/
```

## Resposta de sucesso

Código HTTP:

```http
200 OK
```

Resposta:

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
          "nome": "Carlos Silva"
        },
        "disciplina": {
          "codigo_disciplina": "MAT",
          "nome_disciplina": "Matemática"
        },
        "status": "Não Corrigida",
        "tipo": "Objetiva",
        "serie": 3,
        "bimestre": "1° bimestre",
        "data_de_aplicacao": "2026-08-20",
        "questoes": [
          "66c49f5a2ce79c0f588b1601",
          "66c49f5a2ce79c0f588b1602",
          "66c49f5a2ce79c0f588b1603",
          "66c49f5a2ce79c0f588b1604",
          "66c49f5a2ce79c0f588b1605"
        ]
      }
    ]
  }
}
```

Na resposta:

- `_id` é convertido para string;
- `ativo` não é retornado;
- `questoes` permanece como uma lista de IDs;
- os objetos completos das questões não são incorporados;
- somente provas ativas são retornadas.

## Consulta sem resultados

Código HTTP:

```http
200 OK
```

Resposta:

```json
{
  "sucesso": true,
  "mensagem": "Executado com sucesso",
  "data": {
    "provas": []
  }
}
```

---

# Filtros de consulta

Os filtros são enviados como parâmetros na URL.

## Filtros permitidos

| Parâmetro | Tipo esperado | Campo pesquisado |
|---|---|---|
| `id` | string | `_id` da prova |
| `id_turma` | string | Turma associada |
| `codigo_disciplina` | string | Código da disciplina |
| `nome_disciplina` | string | Nome da disciplina |
| `nome` | string | Nome do professor |
| `status` | string | Status da prova |
| `tipo` | string | Tipo da prova |
| `serie` | inteiro | Série da prova |
| `bimestre` | string | Bimestre |
| `data_de_aplicacao` | string | Data de aplicação |

Os filtros realizam correspondência exata com os valores armazenados.

## Consultar por ID

```http
GET /api/v1/provas/?id=66c4a6c22ce79c0f588b1621
```

O parâmetro público se chama `id`, embora o campo retornado seja `_id`.

Se o valor não possuir um formato válido de `ObjectId`, a API retorna uma lista vazia, sem erro.

## Consultar por turma

```http
GET /api/v1/provas/?id_turma=Turma%202026%20A
```

A consulta funciona tanto quando `id_turma` foi armazenado como string quanto quando foi armazenado como lista contendo a turma informada.

## Consultar por código da disciplina

```http
GET /api/v1/provas/?codigo_disciplina=MAT
```

Internamente, o filtro é aplicado sobre:

```text
disciplina.codigo_disciplina
```

## Consultar por nome da disciplina

```http
GET /api/v1/provas/?nome_disciplina=Matemática
```

Internamente, o filtro é aplicado sobre:

```text
disciplina.nome_disciplina
```

## Consultar por professor

```http
GET /api/v1/provas/?nome=Carlos%20Silva
```

Internamente, o filtro é aplicado sobre:

```text
professor.nome
```

## Consultar por status

```http
GET /api/v1/provas/?status=Não%20Corrigida
```

## Consultar por tipo

```http
GET /api/v1/provas/?tipo=Objetiva
```

## Consultar por série

```http
GET /api/v1/provas/?serie=3
```

A série é convertida para número inteiro antes da pesquisa.

## Consultar por bimestre

```http
GET /api/v1/provas/?bimestre=1°%20bimestre
```

## Consultar por data de aplicação

```http
GET /api/v1/provas/?data_de_aplicacao=2026-08-20
```

## Combinar filtros

É possível combinar diferentes parâmetros:

```http
GET /api/v1/provas/?codigo_disciplina=MAT&tipo=Objetiva&serie=3&status=Não%20Corrigida
```

A prova precisa atender a todos os filtros informados.

## Parâmetro desconhecido

Exemplo:

```http
GET /api/v1/provas/?professor=101
```

Código HTTP:

```http
400 Bad Request
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Parâmetro não permitido: professor",
  "erro": null
}
```

## Série inválida no filtro

Exemplo:

```http
GET /api/v1/provas/?serie=terceira
```

Código HTTP:

```http
400 Bad Request
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "serie inválido: terceira",
  "erro": null
}
```

## ID inválido no filtro

Exemplo:

```http
GET /api/v1/provas/?id=id-invalido
```

Resposta:

```json
{
  "sucesso": true,
  "mensagem": "Executado com sucesso",
  "data": {
    "provas": []
  }
}
```

## Parâmetros vazios

Parâmetros vazios são ignorados.

Exemplo:

```http
GET /api/v1/provas/?status=
```

A requisição possui o mesmo efeito de uma consulta sem esse filtro.

## Provas inativas

As consultas adicionam automaticamente o filtro necessário para ignorar provas com:

```json
{
  "ativo": false
}
```

Não existe um filtro público `ativo`. Portanto, não é possível listar provas inativas por essas rotas.

---

# Atualizar prova

## Rota

```http
PUT /api/v1/provas/{_id}
```

Exemplo:

```http
PUT /api/v1/provas/66c4a6c22ce79c0f588b1621
```

## Cabeçalho

```http
Content-Type: application/json
```

## JSON de entrada

```json
{
  "prova": {
    "id_turma": "Turma 2026 B",
    "professor": {
      "nome": "Carlos Silva"
    },
    "disciplina": {
      "codigo_disciplina": "MAT",
      "nome_disciplina": "Matemática"
    },
    "status": "Corrigida",
    "tipo": "Objetiva",
    "serie": 3,
    "bimestre": "1° bimestre",
    "data_de_aplicacao": "2026-08-22",
    "questoes": [
      "66c49f5a2ce79c0f588b1601",
      "66c49f5a2ce79c0f588b1602",
      "66c49f5a2ce79c0f588b1603",
      "66c49f5a2ce79c0f588b1604",
      "66c49f5a2ce79c0f588b1605"
    ]
  }
}
```

Todos os campos são obrigatórios.

A atualização não é parcial. É necessário enviar novamente a estrutura completa da prova.

O `_id` não deve ser enviado no corpo. A prova é identificada pelo parâmetro da URL.

As questões devem ser enviadas novamente como uma lista de IDs e passam por todas as validações do cadastro.

## Campos substituídos

A atualização substitui:

- `id_turma`;
- `professor`;
- `disciplina`;
- `status`;
- `tipo`;
- `serie`;
- `bimestre`;
- `data_de_aplicacao`;
- `questoes`.

O `_id` permanece o mesmo.

O campo `ativo` também é preservado.

## Resposta de sucesso

Código HTTP:

```http
200 OK
```

Resposta:

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
      "status": "Corrigida",
      "tipo": "Objetiva",
      "serie": 3,
      "bimestre": "1° bimestre",
      "data_de_aplicacao": "2026-08-22",
      "questoes": [
        "66c49f5a2ce79c0f588b1601",
        "66c49f5a2ce79c0f588b1602",
        "66c49f5a2ce79c0f588b1603",
        "66c49f5a2ce79c0f588b1604",
        "66c49f5a2ce79c0f588b1605"
      ]
    }
  }
}
```

Assim como no cadastro, a resposta é construída a partir dos dados recebidos.

Para obter os dados normalizados e confirmados no banco, consulte a prova com:

```http
GET /api/v1/provas/?id=66c4a6c22ce79c0f588b1621
```

## Prova inexistente ou ID inválido

Código HTTP:

```http
400 Bad Request
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Prova não existe",
  "erro": {
    "mensagem": "A prova com Id fornecido não existe no banco de dados"
  }
}
```

## Prova inativa

Uma prova inativa não pode ser atualizada.

Como o documento ainda existe no banco, a resposta pode seguir o formato:

```json
{
  "sucesso": false,
  "mensagem": "Não foi possível atualizar a prova",
  "erro": null
}
```

Código HTTP:

```http
400 Bad Request
```

## Validações da atualização

Antes de atualizar, a API valida novamente:

- turma;
- nome do professor;
- disciplina;
- status;
- tipo;
- série;
- bimestre;
- data de aplicação;
- quantidade de questões;
- formato dos IDs;
- repetição dos IDs;
- existência e estado das questões;
- compatibilidade do tipo das questões;
- compatibilidade da disciplina das questões.

Se qualquer validação falhar, a prova não é atualizada.

---

# Excluir prova

## Rota

```http
DELETE /api/v1/provas/{_id}
```

Exemplo:

```http
DELETE /api/v1/provas/66c4a6c22ce79c0f588b1621
```

A rota não exige corpo JSON.

## Exclusão lógica

A prova não é removida fisicamente do banco.

A API altera:

```json
{
  "ativo": false
}
```

Depois da exclusão:

- a prova deixa de aparecer nas consultas;
- o documento permanece no banco;
- a prova não pode ser atualizada;
- uma segunda tentativa de exclusão retorna `404`.

## Resposta de sucesso

Código HTTP:

```http
200 OK
```

Resposta:

```json
{
  "sucesso": true,
  "mensagem": "Excluído com sucesso",
  "data": null
}
```

## Prova inexistente, inativa ou ID inválido

Código HTTP:

```http
404 Not Found
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Não existe prova com o id 66c4a6c22ce79c0f588b1621",
  "erro": null
}
```

Para um ID inválido:

```json
{
  "sucesso": false,
  "mensagem": "Não existe prova com o id id-invalido",
  "erro": null
}
```

---

# Formato geral das respostas

## Resposta de sucesso

```json
{
  "sucesso": true,
  "mensagem": "Descrição do resultado",
  "data": {}
}
```

Quando não existem dados adicionais:

```json
{
  "sucesso": true,
  "mensagem": "Excluído com sucesso",
  "data": null
}
```

## Erro do middleware

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "Descrição do campo ausente"
  }
}
```

## Erro de regra de negócio

```json
{
  "sucesso": false,
  "mensagem": "Descrição do erro",
  "erro": {
    "mensagem": "Detalhes do erro"
  }
}
```

## Erro de validação do modelo

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Descrição do erro"
  }
}
```

## Erro interno

Código HTTP:

```http
500 Internal Server Error
```

Resposta:

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

# Fluxo recomendado de utilização

1. Cadastre o professor pelo fluxo de usuários.
2. Cadastre os alunos pelo fluxo de alunos.
3. Cadastre a disciplina e associe sua turma e seus alunos.
4. Cadastre questões no banco de questões.
5. Consulte as questões disponíveis.
6. Selecione pelo menos cinco questões compatíveis com a disciplina e o tipo da prova.
7. Envie somente os IDs das questões no cadastro da prova.
8. Consulte a prova para confirmar os dados armazenados.
9. Atualize a prova enquanto ela estiver ativa.
10. Exclua logicamente a prova quando ela não estiver mais em uso.

## Exemplo de fluxo completo

### Consultar questões objetivas da disciplina

```http
GET /api/v1/questoes/?disciplina=matemática&tipo_questao=Objetiva
```

A partir da resposta, o frontend deve extrair os valores de `_id`.

### Cadastrar prova

```http
POST /api/v1/provas/
```

```json
{
  "prova": {
    "id_turma": "Turma 2026 A",
    "professor": {
      "nome": "Carlos Silva"
    },
    "disciplina": {
      "codigo_disciplina": "MAT",
      "nome_disciplina": "Matemática"
    },
    "status": "Não Corrigida",
    "tipo": "Objetiva",
    "serie": 3,
    "bimestre": "1° bimestre",
    "data_de_aplicacao": "2026-08-20",
    "questoes": [
      "66c49f5a2ce79c0f588b1601",
      "66c49f5a2ce79c0f588b1602",
      "66c49f5a2ce79c0f588b1603",
      "66c49f5a2ce79c0f588b1604",
      "66c49f5a2ce79c0f588b1605"
    ]
  }
}
```

### Consultar prova criada

```http
GET /api/v1/provas/?id=66c4a6c22ce79c0f588b1621
```

### Atualizar status da prova

Embora o objetivo seja alterar o status, a atualização exige o envio da prova completa:

```http
PUT /api/v1/provas/66c4a6c22ce79c0f588b1621
```

```json
{
  "prova": {
    "id_turma": "Turma 2026 A",
    "professor": {
      "nome": "Carlos Silva"
    },
    "disciplina": {
      "codigo_disciplina": "MAT",
      "nome_disciplina": "Matemática"
    },
    "status": "Corrigida",
    "tipo": "Objetiva",
    "serie": 3,
    "bimestre": "1° bimestre",
    "data_de_aplicacao": "2026-08-20",
    "questoes": [
      "66c49f5a2ce79c0f588b1601",
      "66c49f5a2ce79c0f588b1602",
      "66c49f5a2ce79c0f588b1603",
      "66c49f5a2ce79c0f588b1604",
      "66c49f5a2ce79c0f588b1605"
    ]
  }
}
```

### Excluir prova

```http
DELETE /api/v1/provas/66c4a6c22ce79c0f588b1621
```