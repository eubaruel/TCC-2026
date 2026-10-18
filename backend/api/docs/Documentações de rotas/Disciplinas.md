# Fluxo de Disciplinas

Documentação completa das rotas responsáveis pelo cadastro, consulta, atualização e exclusão lógica de disciplinas.

## Endereço-base

```text
http://localhost:8080/api/v1/disciplinas
```

## Resumo das rotas

| Método | Rota | Finalidade |
|---|---|---|
| `POST` | `/api/v1/disciplinas/` | Cadastrar uma disciplina |
| `GET` | `/api/v1/disciplinas/` | Consultar disciplinas |
| `PUT` | `/api/v1/disciplinas/{codigo_disciplina}` | Atualizar uma disciplina |
| `DELETE` | `/api/v1/disciplinas/{codigo_disciplina}` | Desativar uma disciplina |

## Autenticação

Atualmente, as rotas de disciplinas não exigem token JWT.

---

# Estrutura de uma disciplina

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `codigo_disciplina` | string | Sim no cadastro | Código único da disciplina |
| `nome_disciplina` | string | Sim | Nome da disciplina |
| `professor` | objeto | Sim | Professor responsável |
| `professor.registro` | inteiro | Sim | Registro do professor |
| `professor.nome` | string | Sim | Nome completo do professor |
| `turma` | string | Sim | Turma associada à disciplina |
| `alunos` | lista de inteiros | Sim | Matrículas dos alunos associados |
| `ativo` | booleano | Gerenciado pela API | Indica se a disciplina está ativa |

Exemplo de uma disciplina:

```json
{
  "codigo_disciplina": "MAT",
  "nome_disciplina": "Matemática",
  "professor": {
    "registro": 101,
    "nome": "Carlos Silva"
  },
  "turma": "Turma 2026 A",
  "alunos": [
    50280715,
    50280716,
    50280717
  ]
}
```

---

# Regras de negócio

## Código da disciplina

O campo `codigo_disciplina`:

- deve ser uma string;
- não pode ser nulo;
- tem os espaços externos removidos antes de ser armazenado;
- deve ser único;
- é utilizado como identificador da disciplina;
- não pode ser alterado pela rota de atualização;
- é utilizado nas rotas de atualização e exclusão.

Exemplo:

```json
{
  "codigo_disciplina": "MAT"
}
```

Uma disciplina excluída logicamente continua reservando seu código. Portanto, não é possível cadastrar outra disciplina com o mesmo código, mesmo que a disciplina anterior esteja inativa.

A comparação do código é sensível a letras maiúsculas e minúsculas. Dessa maneira, valores como os seguintes são considerados diferentes:

```text
MAT
mat
Mat
```

Recomenda-se que o frontend adote um único padrão, preferencialmente códigos em letras maiúsculas.

## Nome da disciplina

O campo `nome_disciplina`:

- deve ser uma string;
- não pode ser nulo;
- deve possuir pelo menos 3 caracteres;
- tem os espaços externos removidos;
- é normalizado com as iniciais em letras maiúsculas.

Exemplo:

```text
Entrada:  "matemática"
Armazenado: "Matemática"
```

Exemplo válido:

```json
{
  "nome_disciplina": "Matemática"
}
```

Exemplo inválido:

```json
{
  "nome_disciplina": "MA"
}
```

## Professor

O campo `professor` deve ser um objeto contendo:

```json
{
  "registro": 101,
  "nome": "Carlos Silva"
}
```

Os campos `registro` e `nome` são obrigatórios.

### Registro do professor

O campo `professor.registro`:

- deve ser um número inteiro;
- não pode ser nulo.

Exemplo válido:

```json
{
  "registro": 101
}
```

Exemplo inválido:

```json
{
  "registro": "101"
}
```

Atualmente, o fluxo de disciplinas não consulta o cadastro de usuários para verificar se o registro realmente pertence a um professor cadastrado e ativo.

### Nome do professor

O campo `professor.nome`:

- deve ser uma string;
- deve possuir pelo menos 5 caracteres;
- deve conter nome e sobrenome;
- cada parte do nome deve possuir pelo menos 3 caracteres;
- tem os espaços externos removidos;
- é normalizado com as iniciais em letras maiúsculas.

Exemplo:

```text
Entrada:  "carlos da silva"
Armazenado: "Carlos Da Silva"
```

Exemplo válido:

```json
{
  "nome": "Carlos Silva"
}
```

Exemplos inválidos:

```json
{
  "nome": "Carlos"
}
```

```json
{
  "nome": "Ca Silva"
}
```

No segundo exemplo, a parte `Ca` possui menos de 3 caracteres.

## Turma

O campo `turma`:

- deve ser uma string;
- não pode ser nulo;
- deve possuir pelo menos 10 caracteres;
- tem os espaços externos removidos.

Exemplo válido:

```json
{
  "turma": "Turma 2026 A"
}
```

Exemplo inválido:

```json
{
  "turma": "3A"
}
```

Atualmente, o fluxo de disciplinas não consulta outro cadastro para verificar se a turma informada existe.

## Alunos

O campo `alunos`:

- deve ser uma lista;
- não pode ser nulo;
- deve possuir pelo menos uma matrícula;
- deve conter somente números inteiros;
- cada matrícula deve possuir exatamente 8 dígitos.

Exemplo válido:

```json
{
  "alunos": [
    50280715,
    50280716,
    50280717
  ]
}
```

Exemplo inválido por utilizar strings:

```json
{
  "alunos": [
    "50280715",
    "50280716"
  ]
}
```

Exemplo inválido por estar vazio:

```json
{
  "alunos": []
}
```

Exemplo inválido por conter uma matrícula com tamanho incorreto:

```json
{
  "alunos": [
    1234
  ]
}
```

Atualmente:

- a API não verifica se as matrículas pertencem a alunos cadastrados;
- a API não impede matrículas repetidas dentro da lista;
- a ordem das matrículas é preservada;
- a lista completa é armazenada no documento da disciplina.

## Estado ativo

No cadastro, a disciplina é criada automaticamente com:

```json
{
  "ativo": true
}
```

O campo `ativo` não precisa ser enviado pelo frontend.

As consultas retornam apenas disciplinas ativas.

A exclusão é lógica. Isso significa que o documento permanece no banco, mas passa a possuir:

```json
{
  "ativo": false
}
```

Uma disciplina inativa:

- não aparece nas consultas;
- não pode ser atualizada;
- não pode ser excluída novamente;
- continua impedindo o cadastro de outra disciplina com o mesmo código.

## Campos adicionais

Campos adicionais enviados no JSON não são utilizados na criação ou atualização do documento.

Recomenda-se que o frontend envie somente os campos documentados.

---

# Cadastrar disciplina

## Rota

```http
POST /api/v1/disciplinas/
```

## Cabeçalho

```http
Content-Type: application/json
```

## JSON de entrada

```json
{
  "disciplina": {
    "codigo_disciplina": "MAT",
    "nome_disciplina": "Matemática",
    "professor": {
      "registro": 101,
      "nome": "Carlos Silva"
    },
    "turma": "Turma 2026 A",
    "alunos": [
      50280715,
      50280716,
      50280717
    ]
  }
}
```

Todos os campos apresentados são obrigatórios.

O campo `ativo` não deve ser enviado. A API atribui automaticamente o valor `true`.

## Resposta de sucesso

Código HTTP:

```http
201 Created
```

Corpo da resposta:

```json
{
  "sucesso": true,
  "mensagem": "Cadastro realizado com sucesso",
  "data": {
    "disciplina": {
      "codigo_disciplina": "MAT",
      "nome_disciplina": "Matemática",
      "turma": "Turma 2026 A",
      "alunos": [
        50280715,
        50280716,
        50280717
      ],
      "professor": {
        "registro": 101,
        "nome": "Carlos Silva"
      }
    }
  }
}
```

A resposta do cadastro é construída a partir dos dados recebidos. Por isso, ela pode não apresentar algumas normalizações realizadas antes do armazenamento, como a capitalização do nome da disciplina e do professor.

Para obter a representação armazenada e normalizada, realize posteriormente uma consulta `GET`.

## Possíveis erros

### Chave `disciplina` ausente

Código HTTP:

```http
400 Bad Request
```

Exemplo de entrada inválida:

```json
{
  "codigo_disciplina": "MAT"
}
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'disciplina' é obrigatório!"
  }
}
```

### Campo obrigatório ausente

Exemplo sem o campo `turma`:

```json
{
  "disciplina": {
    "codigo_disciplina": "MAT",
    "nome_disciplina": "Matemática",
    "professor": {
      "registro": 101,
      "nome": "Carlos Silva"
    },
    "alunos": [
      50280715
    ]
  }
}
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'turma' é obrigatório!"
  }
}
```

### Campo obrigatório do professor ausente

Exemplo:

```json
{
  "disciplina": {
    "codigo_disciplina": "MAT",
    "nome_disciplina": "Matemática",
    "professor": {
      "nome": "Carlos Silva"
    },
    "turma": "Turma 2026 A",
    "alunos": [
      50280715
    ]
  }
}
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'registro' do professor é obrigatório!"
  }
}
```

### Código repetido

Código HTTP:

```http
400 Bad Request
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Código repetido",
  "erro": {
    "mensagem": "A disciplina com o código MAT já está cadastrado"
  }
}
```

### Nome da disciplina inválido

Exemplo:

```json
{
  "nome_disciplina": "MA"
}
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Nome da disciplina deve ter ao menos 3 caracteres"
  }
}
```

### Professor inválido

Exemplo de registro enviado como string:

```json
{
  "professor": {
    "registro": "101",
    "nome": "Carlos Silva"
  }
}
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Registro do funcionário deve ser um int"
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

### Lista de alunos vazia

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Lista de alunos não pode ser vazia"
  }
}
```

### Matrícula inválida na lista

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Matrícula deve ter 8 dígitos"
  }
}
```

---

# Consultar disciplinas

## Rota

```http
GET /api/v1/disciplinas/
```

A rota não exige corpo JSON.

## Consultar todas as disciplinas

```http
GET /api/v1/disciplinas/
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
    "disciplinas": [
      {
        "codigo_disciplina": "MAT",
        "nome_disciplina": "Matemática",
        "professor": {
          "registro": 101,
          "nome": "Carlos Silva"
        },
        "turma": "Turma 2026 A",
        "quantidade_alunos": 3
      }
    ]
  }
}
```

Na resposta da consulta:

- o campo interno `_id` do MongoDB não é retornado;
- o campo `ativo` não é retornado;
- a lista `alunos` não é retornada;
- a lista `alunos` é substituída pelo campo `quantidade_alunos`;
- somente disciplinas ativas são retornadas.

## Consulta sem resultados

Quando nenhuma disciplina corresponde à pesquisa, a requisição continua sendo considerada bem-sucedida.

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
    "disciplinas": []
  }
}
```

---

# Filtros de consulta

Os filtros devem ser enviados como parâmetros na URL.

## Filtros permitidos

| Parâmetro | Tipo esperado | Campo pesquisado |
|---|---|---|
| `codigo_disciplina` | string | Código da disciplina |
| `nome_disciplina` | string | Nome da disciplina |
| `registro` | inteiro | Registro do professor |
| `nome` | string | Nome do professor |
| `turma` | string | Turma da disciplina |
| `alunos` | inteiro | Matrícula presente na lista de alunos |

Os filtros realizam correspondência exata com os valores armazenados no banco.

## Consultar por código

```http
GET /api/v1/disciplinas/?codigo_disciplina=MAT
```

## Consultar por nome da disciplina

```http
GET /api/v1/disciplinas/?nome_disciplina=Matemática
```

Como o nome é armazenado com iniciais maiúsculas, recomenda-se utilizar o mesmo formato na consulta.

## Consultar por registro do professor

```http
GET /api/v1/disciplinas/?registro=101
```

O valor é convertido para um número inteiro antes da pesquisa.

Internamente, o filtro é aplicado sobre:

```text
professor.registro
```

## Consultar por nome do professor

```http
GET /api/v1/disciplinas/?nome=Carlos%20Silva
```

Internamente, o filtro é aplicado sobre:

```text
professor.nome
```

## Consultar por turma

```http
GET /api/v1/disciplinas/?turma=Turma%202026%20A
```

## Consultar por matrícula de aluno

```http
GET /api/v1/disciplinas/?alunos=50280715
```

O valor é convertido para número inteiro.

Como `alunos` é uma lista no MongoDB, a consulta retorna as disciplinas cuja lista contém a matrícula informada.

A lista completa de matrículas não é retornada. A resposta apresenta somente `quantidade_alunos`.

## Combinar filtros

É possível combinar diferentes filtros na mesma requisição:

```http
GET /api/v1/disciplinas/?codigo_disciplina=MAT&registro=101&turma=Turma%202026%20A
```

Nesse caso, a disciplina precisa atender a todos os filtros.

## Parâmetro desconhecido

Exemplo:

```http
GET /api/v1/disciplinas/?email=professor@example.com
```

Código HTTP:

```http
400 Bad Request
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Parâmetro não permitido: email",
  "erro": null
}
```

## Registro inválido

Exemplo:

```http
GET /api/v1/disciplinas/?registro=abc
```

Código HTTP:

```http
400 Bad Request
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "registro inválido: abc",
  "erro": null
}
```

## Matrícula inválida no filtro

Exemplo:

```http
GET /api/v1/disciplinas/?alunos=abc
```

Código HTTP:

```http
400 Bad Request
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "alunos inválido: abc",
  "erro": null
}
```

## Parâmetros vazios

Parâmetros cujo valor esteja vazio são ignorados.

Exemplo:

```http
GET /api/v1/disciplinas/?nome_disciplina=
```

Essa requisição possui o mesmo efeito de uma consulta sem esse filtro.

## Disciplinas inativas

Não existe um filtro público `ativo` no fluxo de disciplinas.

As consultas adicionam automaticamente o filtro necessário para ignorar documentos com:

```json
{
  "ativo": false
}
```

Portanto, não é possível consultar disciplinas inativas por essas rotas.

---

# Atualizar disciplina

## Rota

```http
PUT /api/v1/disciplinas/{codigo_disciplina}
```

Exemplo:

```http
PUT /api/v1/disciplinas/MAT
```

O código informado na URL identifica a disciplina que será atualizada.

## Cabeçalho

```http
Content-Type: application/json
```

## JSON de entrada

```json
{
  "disciplina": {
    "nome_disciplina": "Matemática Aplicada",
    "professor": {
      "registro": 102,
      "nome": "Marcos Souza"
    },
    "turma": "Turma 2026 B",
    "alunos": [
      50280715,
      50280716,
      50280718
    ]
  }
}
```

Todos os campos apresentados são obrigatórios.

O campo `codigo_disciplina` não precisa ser enviado no corpo. O código da disciplina é obtido pela URL.

A atualização substitui os seguintes dados:

- `nome_disciplina`;
- `professor`;
- `turma`;
- `alunos`.

O código permanece o mesmo.

## Resposta de sucesso

Código HTTP:

```http
200 OK
```

Resposta atual da API:

```json
{
  "sucesso": true,
  "mensagem": "Atualizado com sucesso",
  "data": {
    "disciplina": {
      "codigo_disciplina": null,
      "nome_disciplina": "Matemática Aplicada",
      "turma": "Turma 2026 B",
      "alunos": [
        50280715,
        50280716,
        50280718
      ],
      "professor": {
        "registro": 102,
        "nome": "Marcos Souza"
      }
    }
  }
}
```

Atualmente, `codigo_disciplina` aparece como `null` nessa resposta quando ele não é enviado no corpo.

Isso acontece somente na formatação da resposta. A disciplina correta é localizada e atualizada no banco utilizando o código presente na URL.

Para obter a representação armazenada depois da atualização, consulte:

```http
GET /api/v1/disciplinas/?codigo_disciplina=MAT
```

## Código enviado no corpo

O identificador utilizado para localizar e atualizar a disciplina sempre é o código presente na URL.

Portanto, o formato recomendado é não enviar `codigo_disciplina` no corpo da atualização.

## Disciplina inexistente ou inativa

Código HTTP:

```http
404 Not Found
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Disciplina não encontrada",
  "erro": "Não foi possível atualizar a disciplina com o código MAT"
}
```

Uma disciplina excluída logicamente também produz essa resposta, pois somente disciplinas ativas podem ser atualizadas.

## Chave `disciplina` ausente

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'disciplina' é obrigatório!"
  }
}
```

## Campo obrigatório ausente

Exemplo sem `alunos`:

```json
{
  "disciplina": {
    "nome_disciplina": "Matemática Aplicada",
    "professor": {
      "registro": 102,
      "nome": "Marcos Souza"
    },
    "turma": "Turma 2026 B"
  }
}
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'alunos' é obrigatório!"
  }
}
```

## Validações da atualização

A atualização utiliza as mesmas validações do cadastro para:

- nome da disciplina;
- professor;
- turma;
- matrículas dos alunos.

Não é possível realizar uma atualização parcial. Todos os campos exigidos precisam ser enviados.

## Estado ativo na atualização

O campo `ativo` não faz parte dos campos atualizáveis do fluxo de disciplinas.

Uma disciplina inativa não pode ser reativada por essa rota.

---

# Excluir disciplina

## Rota

```http
DELETE /api/v1/disciplinas/{codigo_disciplina}
```

Exemplo:

```http
DELETE /api/v1/disciplinas/MAT
```

A rota não exige corpo JSON.

## Exclusão lógica

A disciplina não é removida fisicamente do banco.

A API altera o campo:

```json
{
  "ativo": false
}
```

Depois da exclusão:

- a disciplina deixa de aparecer nas consultas;
- seu código continua armazenado;
- o código não pode ser utilizado em um novo cadastro;
- a disciplina não pode ser atualizada;
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

## Disciplina inexistente ou já inativa

Código HTTP:

```http
404 Not Found
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Disciplina não encontrada",
  "erro": "Não existe disciplina com o código MAT"
}
```

---

# Formato geral das respostas

## Resposta de sucesso

As respostas de sucesso seguem a estrutura:

```json
{
  "sucesso": true,
  "mensagem": "Descrição do resultado",
  "data": {}
}
```

Quando a rota não precisa retornar dados, o campo `data` possui o valor `null`:

```json
{
  "sucesso": true,
  "mensagem": "Excluído com sucesso",
  "data": null
}
```

## Erro de validação do middleware

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "Descrição do campo ausente"
  }
}
```

## Erro de validação do modelo

Erros de tipo, tamanho ou formato seguem a estrutura:

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

1. Cadastre os professores pelo fluxo de usuários.
2. Cadastre ou importe os alunos pelo fluxo de alunos.
3. Envie o cadastro da disciplina com o professor e as matrículas dos alunos.
4. Consulte a disciplina para confirmar os dados normalizados e a quantidade de alunos.
5. Utilize o código da disciplina ao criar provas relacionadas a ela.
6. Atualize a lista de alunos ou o professor quando necessário.
7. Exclua logicamente a disciplina quando ela não estiver mais em uso.

## Exemplo de fluxo completo

### Cadastro

```http
POST /api/v1/disciplinas/
```

```json
{
  "disciplina": {
    "codigo_disciplina": "MAT",
    "nome_disciplina": "Matemática",
    "professor": {
      "registro": 101,
      "nome": "Carlos Silva"
    },
    "turma": "Turma 2026 A",
    "alunos": [
      50280715,
      50280716,
      50280717
    ]
  }
}
```

### Consulta

```http
GET /api/v1/disciplinas/?codigo_disciplina=MAT
```

### Atualização

```http
PUT /api/v1/disciplinas/MAT
```

```json
{
  "disciplina": {
    "nome_disciplina": "Matemática Aplicada",
    "professor": {
      "registro": 102,
      "nome": "Marcos Souza"
    },
    "turma": "Turma 2026 B",
    "alunos": [
      50280715,
      50280716,
      50280718
    ]
  }
}
```

### Exclusão lógica

```http
DELETE /api/v1/disciplinas/MAT
```