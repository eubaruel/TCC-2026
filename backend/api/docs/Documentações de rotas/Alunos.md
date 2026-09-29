# Fluxo de Alunos

Documentação completa das rotas responsáveis pelo cadastro, importação por planilha, consulta, atualização e exclusão lógica de alunos.

## Endereço-base

```text
http://localhost:8080/api/v1/alunos
```

## Resumo das rotas

| Método | Rota | Finalidade |
|---|---|---|
| `POST` | `/api/v1/alunos/` | Cadastrar um aluno |
| `POST` | `/api/v1/alunos/excel` | Importar alunos por planilha |
| `GET` | `/api/v1/alunos/` | Consultar alunos |
| `PUT` | `/api/v1/alunos/{matricula_aluno}` | Atualizar um aluno |
| `DELETE` | `/api/v1/alunos/{matricula_aluno}` | Desativar um aluno |

## Autenticação

Atualmente, as rotas de alunos não exigem token JWT.

---

# Estrutura de um aluno

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `matricula_aluno` | inteiro | Sim no cadastro | Matrícula com exatamente 8 dígitos |
| `nome_aluno` | string | Sim | Nome completo do aluno |
| `turma` | string | Sim | Turma à qual o aluno pertence |
| `serie` | inteiro | Sim | Série atual do aluno |
| `situacao` | string | Sim | Situação acadêmica |
| `email_aluno` | string | Sim | Endereço de e-mail do aluno |
| `ativo` | booleano | Somente na atualização | Indica se o aluno está ativo |

---

# Regras de negócio

## Matrícula

O campo `matricula_aluno`:

- deve ser um número inteiro;
- deve possuir exatamente 8 dígitos;
- deve ser único;
- não pode ser alterado depois do cadastro;
- é utilizado como identificador do aluno nas rotas de atualização e exclusão.

Exemplo válido:

```json
{
  "matricula_aluno": 50280715
}
```

Exemplos inválidos:

```json
{
  "matricula_aluno": 123
}
```

```json
{
  "matricula_aluno": "50280715"
}
```

A matrícula deve ser enviada como número inteiro, não como string.

Uma matrícula pertencente a um aluno inativo também é considerada cadastrada e não pode ser reutilizada em um novo cadastro.

## Nome

O campo `nome_aluno`:

- deve ser uma string;
- deve possuir pelo menos 5 caracteres;
- deve conter nome e sobrenome;
- cada parte do nome deve possuir pelo menos 2 caracteres;
- é normalizado para iniciais maiúsculas.

Exemplo:

```text
Entrada:  "josé da silva"
Saída:    "José Da Silva"
```

## Turma

O campo `turma`:

- deve ser uma string;
- deve possuir pelo menos 10 caracteres;
- tem espaços externos removidos.

Exemplo:

```json
{
  "turma": "Turma 2026 A"
}
```

## Série

O campo `serie`:

- deve ser um número inteiro;
- deve ser maior que zero.

Exemplo:

```json
{
  "serie": 3
}
```

## Situação

O campo `situacao`:

- deve ser uma string;
- deve conter pelo menos uma letra;
- não pode possuir números.

Exemplos válidos:

```text
Matriculado
Pre-Mat
Transferido
```

Exemplos inválidos:

```text
123
Matriculado 2026
```

## E-mail

O campo `email_aluno`:

- deve ser uma string;
- deve possuir entre 5 e 150 caracteres;
- deve seguir um formato válido de e-mail;
- tem espaços externos removidos.

Exemplo:

```json
{
  "email_aluno": "aluno@example.com"
}
```

O e-mail é armazenado no banco, mas não aparece nas respostas das consultas `GET`.

## Estado ativo

No cadastro individual e na importação por planilha, o aluno é criado automaticamente com:

```json
{
  "ativo": true
}
```

O campo `ativo` não deve ser enviado no cadastro individual.

Na atualização, o campo é obrigatório e pode ser utilizado para ativar ou desativar o aluno.

---

# Cadastrar aluno

## Rota

```http
POST /api/v1/alunos/
```

## Cabeçalho

```http
Content-Type: application/json
```

## JSON de entrada

```json
{
  "aluno": {
    "matricula_aluno": 50280715,
    "nome_aluno": "José da Silva",
    "turma": "Turma 2026 A",
    "serie": 3,
    "situacao": "Pre-Mat",
    "email_aluno": "jose@example.com"
  }
}
```

Todos os campos apresentados são obrigatórios.

O campo `ativo` não deve ser enviado. A API atribui automaticamente o valor `true`.

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
    "aluno": {
      "matricula_aluno": 50280715,
      "nome_aluno": "José da Silva",
      "turma": "Turma 2026 A",
      "serie": 3,
      "situacao": "Pre-Mat",
      "email_aluno": "jose@example.com",
      "ativo": true
    }
  }
}
```

## Possíveis erros

### Chave `aluno` ausente

Código HTTP:

```text
400 Bad Request
```

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'aluno' é obrigatório!"
  }
}
```

### Campo obrigatório ausente

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'matricula_aluno' é obrigatório!"
  }
}
```

### Matrícula repetida

```json
{
  "sucesso": false,
  "mensagem": "Matrícula repetida",
  "erro": {
    "mensagem": "O aluno com a matrícula 50280715 já está cadastrado"
  }
}
```

### Matrícula inválida

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Matrícula deve ter 8 dígitos"
  }
}
```

### Nome inválido

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Nome do aluno deve ter ao menos um sobrenome"
  }
}
```

### E-mail inválido

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Email inválido"
  }
}
```

---

# Importar alunos por planilha

## Rota

```http
POST /api/v1/alunos/excel
```

Essa rota não recebe JSON.

O arquivo deve ser enviado como `multipart/form-data`.

## Cabeçalho

```http
Content-Type: multipart/form-data
```

## Campo do arquivo

Recomenda-se utilizar o nome:

```text
arquivo
```

Exemplo conceitual:

```text
arquivo: alunos.xlsx
```

A implementação utiliza o primeiro arquivo encontrado na requisição. Ainda assim, recomenda-se manter o nome `arquivo` como padrão.

## Exemplo com cURL

```bash
curl -X POST \
  http://localhost:8080/api/v1/alunos/excel \
  -F "arquivo=@alunos.xlsx"
```

## Formato do arquivo

O arquivo:

- deve possuir a extensão `.xlsx`;
- deve conter todas as colunas obrigatórias;
- não pode possuir linhas com valores nulos;
- não pode possuir matrículas repetidas dentro da própria planilha.

A extensão é verificada de forma sensível a letras maiúsculas e minúsculas.

Utilize:

```text
alunos.xlsx
```

Evite:

```text
alunos.XLSX
```

## Colunas obrigatórias

Os nomes devem ser enviados exatamente como apresentados:

| Coluna | Tipo esperado | Campo correspondente |
|---|---|---|
| `matrícula` | inteiro | `matricula_aluno` |
| `nome` | string | `nome_aluno` |
| `turma` | string | `turma` |
| `série` | inteiro | `serie` |
| `situação` | string | `situacao` |
| `email` | string | `email_aluno` |

Os acentos fazem parte dos nomes das colunas.

## Exemplo da planilha

| matrícula | nome | turma | série | situação | email |
|---:|---|---|---:|---|---|
| 50280715 | José da Silva | Turma 2026 A | 3 | Pre-Mat | jose@example.com |
| 50280716 | Maria de Souza | Turma 2026 A | 3 | Matriculado | maria@example.com |

## Validações da importação

Antes de escrever no banco, a API valida todas as linhas.

São verificados:

- presença das colunas obrigatórias;
- existência de valores nulos;
- formato da matrícula;
- quantidade de dígitos da matrícula;
- nome e sobrenome;
- tamanho mínimo da turma;
- formato da série;
- conteúdo da situação;
- formato do e-mail;
- matrículas repetidas dentro da planilha.

Se qualquer linha possuir erro:

- nenhuma linha é importada;
- a API retorna a lista dos erros encontrados;
- no máximo 50 erros são incluídos na resposta;
- `total_erros` informa a quantidade total detectada.

## Comportamento no banco

A importação utiliza `upsert` pela matrícula:

- matrícula inexistente: cria o aluno;
- matrícula existente: atualiza o aluno;
- aluno importado recebe `ativo: true`;
- um aluno inativo pode ser reativado pela importação.

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
    "importacao": {
      "processados": 2,
      "criados": 1,
      "atualizados": 1
    }
  }
}
```

### Significado dos campos

| Campo | Descrição |
|---|---|
| `processados` | Quantidade total de alunos válidos enviados ao banco |
| `criados` | Quantidade de novos documentos criados |
| `atualizados` | Quantidade de documentos existentes que foram modificados |

Um documento existente que já possua exatamente os mesmos dados pode ser processado sem aumentar `atualizados`.

## Possíveis erros

### Arquivo não enviado

```json
{
  "sucesso": false,
  "mensagem": "Arquivo não enviado",
  "erro": "O arquivo excel não foi enviado na requisição"
}
```

Código HTTP:

```text
400 Bad Request
```

### Extensão inválida

```json
{
  "sucesso": false,
  "mensagem": "Formato inválido",
  "erro": "O tipo de arquivo deve ser .xlsx"
}
```

### Coluna obrigatória ausente

```json
{
  "sucesso": false,
  "mensagem": "Planilha inválida",
  "erro": {
    "mensagem": "Colunas ausentes: email, situação"
  }
}
```

### Dados inválidos nas linhas

```json
{
  "sucesso": false,
  "mensagem": "Planilha contém dados inválidos",
  "erro": {
    "erros": [
      "Linha 2: Matrícula deve ter 8 dígitos",
      "Linha 3: Email inválido",
      "Linha 4: matrícula 50280715 repetida na planilha"
    ],
    "total_erros": 3
  }
}
```

### Planilha vazia

```json
{
  "sucesso": false,
  "mensagem": "Planilha vazia",
  "erro": {
    "mensagem": "Nenhum aluno válido foi encontrado"
  }
}
```

---

# Consultar alunos

## Rota

```http
GET /api/v1/alunos/
```

A requisição não possui corpo JSON.

## Consultar todos os alunos

```http
GET /api/v1/alunos/
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
    "alunos": [
      {
        "matricula_aluno": 50280715,
        "nome_aluno": "José Da Silva",
        "turma": "Turma 2026 A",
        "serie": 3,
        "situacao": "Pre-Mat",
        "ativo": true
      }
    ]
  }
}
```

A consulta não retorna:

```text
_id
email_aluno
```

O campo `email_aluno` permanece armazenado no banco, mas é omitido da resposta.

## Alunos inativos

A consulta sem filtros pode retornar alunos ativos e inativos.

Para consultar somente alunos ativos:

```http
GET /api/v1/alunos/?ativo=true
```

Para consultar somente alunos inativos:

```http
GET /api/v1/alunos/?ativo=false
```

## Consulta sem resultados

Uma consulta sem resultados retorna HTTP `200` e uma lista vazia:

```json
{
  "sucesso": true,
  "mensagem": "Executado com sucesso",
  "data": {
    "alunos": []
  }
}
```

---

# Filtros de consulta

Os filtros são enviados por query parameters.

## Filtros permitidos

| Parâmetro | Tipo | Comportamento |
|---|---|---|
| `matricula_aluno` | inteiro | Correspondência exata |
| `nome_aluno` | string | Correspondência exata |
| `turma` | string | Correspondência exata |
| `serie` | inteiro | Correspondência exata |
| `situacao` | string | Correspondência exata |
| `ativo` | booleano | Correspondência exata |

Os filtros podem ser combinados.

As consultas utilizam correspondência exata. Não existe busca parcial por nome.

## Consultar por matrícula

```http
GET /api/v1/alunos/?matricula_aluno=50280715
```

## Consultar por nome

```http
GET /api/v1/alunos/?nome_aluno=José%20Da%20Silva
```

## Consultar por turma

```http
GET /api/v1/alunos/?turma=Turma%202026%20A
```

## Consultar por série

```http
GET /api/v1/alunos/?serie=3
```

## Consultar por situação

```http
GET /api/v1/alunos/?situacao=Pre-Mat
```

## Consultar por estado

Valores aceitos como verdadeiro:

```text
true
1
```

Valores aceitos como falso:

```text
false
0
```

Exemplos:

```http
GET /api/v1/alunos/?ativo=true
```

```http
GET /api/v1/alunos/?ativo=0
```

## Combinar filtros

```http
GET /api/v1/alunos/?turma=Turma%202026%20A&serie=3&ativo=true
```

## Parâmetro desconhecido

Exemplo inválido:

```http
GET /api/v1/alunos/?email_aluno=jose@example.com
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Parâmetro não permitido: email_aluno",
  "erro": null
}
```

Código HTTP:

```text
400 Bad Request
```

## Valor booleano inválido

Exemplo:

```http
GET /api/v1/alunos/?ativo=sim
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "ativo inválido: sim",
  "erro": null
}
```

---

# Atualizar aluno

## Rota

```http
PUT /api/v1/alunos/{matricula_aluno}
```

Exemplo:

```http
PUT /api/v1/alunos/50280715
```

A matrícula é enviada na URL e não pode ser alterada pelo JSON.

A atualização é completa. Todos os campos apresentados abaixo são obrigatórios.

## JSON de entrada

```json
{
  "aluno": {
    "nome_aluno": "José da Silva",
    "turma": "Turma 2026 B",
    "serie": 3,
    "situacao": "Matriculado",
    "email_aluno": "jose.silva@example.com",
    "ativo": true
  }
}
```

O campo abaixo não precisa ser enviado:

```text
matricula_aluno
```

Caso seja enviado, ele não é utilizado para definir qual aluno será atualizado. A matrícula utilizada é a da URL.

## Campo `ativo`

O campo `ativo` é obrigatório na atualização.

Para manter ou reativar o aluno:

```json
{
  "ativo": true
}
```

Para desativar o aluno:

```json
{
  "ativo": false
}
```

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
    "aluno": {
      "matricula_aluno": null,
      "nome_aluno": "José da Silva",
      "turma": "Turma 2026 B",
      "serie": 3,
      "situacao": "Matriculado",
      "email_aluno": "jose.silva@example.com",
      "ativo": true
    }
  }
}
```

> **Observação:** na implementação atual, `matricula_aluno` aparece como `null` na resposta do `PUT` porque a matrícula é recebida pela URL e o formatador da resposta lê somente o JSON. A matrícula armazenada no banco não é alterada.

Para consultar o registro atualizado com sua matrícula, utilize:

```http
GET /api/v1/alunos/?matricula_aluno=50280715
```

## Aluno inexistente

Código HTTP:

```text
400 Bad Request
```

```json
{
  "sucesso": false,
  "mensagem": "Aluno não encontrado",
  "erro": {
    "mensagem": "O aluno com a matrícula 50280715 não está cadastrado"
  }
}
```

## Campo obrigatório ausente

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'ativo' é obrigatório!"
  }
}
```

## Matrícula inválida na URL

A rota exige um número inteiro:

```http
PUT /api/v1/alunos/50280715
```

Uma URL com letras não corresponde à rota:

```http
PUT /api/v1/alunos/ABC
```

Nesse caso, a API retorna HTTP `404`.

---

# Excluir aluno

## Rota

```http
DELETE /api/v1/alunos/{matricula_aluno}
```

Exemplo:

```http
DELETE /api/v1/alunos/50280715
```

A requisição não possui corpo JSON.

## Exclusão lógica

O aluno não é removido fisicamente do MongoDB.

O documento é atualizado para:

```json
{
  "ativo": false
}
```

Os demais dados permanecem armazenados.

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

## Aluno inexistente ou já inativo

Código HTTP:

```text
404 Not Found
```

```json
{
  "sucesso": false,
  "mensagem": "Aluno não encontrado",
  "erro": "Não existe aluno com a matrícula 50280715"
}
```

Uma segunda tentativa de exclusão do mesmo aluno também pode retornar `404`, pois o documento já estará inativo e nenhuma nova modificação será realizada.

## Reativar aluno

Um aluno inativo pode ser reativado por meio de:

- atualização com `ativo: true`;
- nova importação por planilha com a mesma matrícula.

Exemplo:

```http
PUT /api/v1/alunos/50280715
```

```json
{
  "aluno": {
    "nome_aluno": "José da Silva",
    "turma": "Turma 2026 A",
    "serie": 3,
    "situacao": "Matriculado",
    "email_aluno": "jose@example.com",
    "ativo": true
  }
}
```

---

# Formato geral dos erros de validação

Erros de tipo ou regras dos modelos retornam:

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

1. Cadastre alunos individualmente com `POST /api/v1/alunos/`.
2. Para cadastros em massa, utilize `POST /api/v1/alunos/excel`.
3. Consulte os alunos ativos com `GET /api/v1/alunos/?ativo=true`.
4. Utilize a matrícula como identificador do aluno.
5. Atualize os dados com `PUT /api/v1/alunos/{matricula_aluno}`.
6. Desative um aluno com `DELETE /api/v1/alunos/{matricula_aluno}`.
7. Reative um aluno com `PUT` ou por uma nova importação.

## Exemplo de fluxo completo

### Cadastro

```http
POST /api/v1/alunos/
```

```json
{
  "aluno": {
    "matricula_aluno": 50280715,
    "nome_aluno": "José da Silva",
    "turma": "Turma 2026 A",
    "serie": 3,
    "situacao": "Pre-Mat",
    "email_aluno": "jose@example.com"
  }
}
```

### Consulta

```http
GET /api/v1/alunos/?matricula_aluno=50280715
```

### Atualização

```http
PUT /api/v1/alunos/50280715
```

```json
{
  "aluno": {
    "nome_aluno": "José da Silva",
    "turma": "Turma 2026 A",
    "serie": 3,
    "situacao": "Matriculado",
    "email_aluno": "jose@example.com",
    "ativo": true
  }
}
```

### Exclusão lógica

```http
DELETE /api/v1/alunos/50280715
```