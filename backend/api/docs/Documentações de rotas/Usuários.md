# Fluxo de Usuários

Documentação completa das rotas responsáveis pelo cadastro, importação por planilha, autenticação, consulta, atualização e exclusão lógica de usuários.

## Endereço-base

```text
http://localhost:8080/api/v1/usuarios
```

## Resumo das rotas

| Método | Rota | Finalidade |
|---|---|---|
| `POST` | `/api/v1/usuarios/login` | Autenticar um usuário |
| `POST` | `/api/v1/usuarios/` | Cadastrar um usuário |
| `POST` | `/api/v1/usuarios/excel` | Importar usuários por planilha |
| `GET` | `/api/v1/usuarios/` | Consultar usuários |
| `PUT` | `/api/v1/usuarios/{registro}` | Atualizar um usuário |
| `DELETE` | `/api/v1/usuarios/{registro}` | Desativar um usuário |

## Autenticação

Atualmente, o login valida o registro e a senha, mas ainda não gera um token JWT.

As demais rotas também não exigem token JWT neste momento.

---

# Estrutura de um usuário

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `registro` | inteiro | Sim no cadastro | Identificador do funcionário |
| `nome` | string | Sim | Nome completo do usuário |
| `email` | string | Sim | Endereço de e-mail |
| `senha` | string | Sim no cadastro e login | Senha do usuário |
| `role` | string | Sim | Papel do usuário no sistema |
| `ativo` | booleano | Sim na atualização | Indica se o usuário está ativo |

Exemplo:

```json
{
  "registro": 101,
  "nome": "Carlos Silva",
  "email": "carlos@example.com",
  "role": "Professor",
  "ativo": true
}
```

A senha nunca é retornada pelas rotas de consulta, cadastro, atualização ou login.

---

# Regras de negócio

## Registro

O campo `registro`:

- deve ser um número inteiro;
- não pode ser nulo;
- deve ser único;
- identifica o usuário;
- não pode ser alterado depois do cadastro;
- é utilizado nas rotas de atualização e exclusão.

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

Atualmente, não existe validação de quantidade mínima ou máxima de dígitos para o registro.

Um registro pertencente a um usuário inativo continua sendo considerado cadastrado e não pode ser reutilizado em um novo cadastro.

## Nome

O campo `nome`:

- deve ser uma string;
- não pode ser nulo;
- deve possuir pelo menos 5 caracteres;
- deve conter nome e sobrenome;
- cada parte do nome deve possuir pelo menos 3 caracteres;
- tem os espaços externos removidos;
- é armazenado com as iniciais em letras maiúsculas.

Exemplo:

```text
Entrada:    "carlos da silva"
Armazenado: "Carlos Da Silva"
```

Exemplo válido:

```json
{
  "nome": "Carlos Silva"
}
```

Exemplo inválido por não possuir sobrenome:

```json
{
  "nome": "Carlos"
}
```

Exemplo inválido por possuir uma parte com menos de 3 caracteres:

```json
{
  "nome": "Ca Silva"
}
```

## E-mail

O campo `email`:

- deve ser uma string;
- não pode ser nulo;
- deve possuir entre 5 e 150 caracteres;
- deve seguir um formato válido de e-mail;
- tem os espaços externos removidos;
- é armazenado em letras minúsculas.

Exemplo:

```text
Entrada:    "CARLOS@EXAMPLE.COM"
Armazenado: "carlos@example.com"
```

Exemplo válido:

```json
{
  "email": "carlos@example.com"
}
```

Exemplos inválidos:

```json
{
  "email": "carlos"
}
```

```json
{
  "email": "@example.com"
}
```

Atualmente, o e-mail não precisa ser único. A unicidade é aplicada somente ao registro.

## Senha

A senha:

- deve ser uma string;
- não pode ser nula;
- deve possuir pelo menos 6 caracteres;
- deve conter pelo menos uma letra maiúscula;
- deve conter pelo menos um número;
- deve conter pelo menos um caractere especial;
- tem os espaços externos removidos;
- é transformada em hash antes de ser armazenada.

Caracteres especiais reconhecidos:

```text
! @ # $ % ^ & * ( ) , . ? " : { } | < >
```

Exemplo válido:

```json
{
  "senha": "Senha@123"
}
```

Exemplo inválido sem letra maiúscula:

```json
{
  "senha": "senha@123"
}
```

Exemplo inválido sem número:

```json
{
  "senha": "Senha@abc"
}
```

Exemplo inválido sem caractere especial:

```json
{
  "senha": "Senha123"
}
```

A senha original não é armazenada no banco.

O documento mantém somente o hash gerado pelo `bcrypt`.

## Papel do usuário

O campo `role` aceita somente:

```text
Professor
Processo pedagógico
```

Exemplos:

```json
{
  "role": "Professor"
}
```

```json
{
  "role": "Processo pedagógico"
}
```

O valor:

- deve ser uma string;
- não pode ser nulo;
- não pode ser vazio;
- tem os espaços externos removidos;
- é normalizado antes da validação.

Exemplo:

```text
Entrada:    "professor"
Armazenado: "Professor"
```

Qualquer valor diferente dos dois papéis permitidos é rejeitado.

## Estado ativo

No cadastro individual, o usuário é criado automaticamente com:

```json
{
  "ativo": true
}
```

O campo `ativo` não precisa ser enviado no cadastro.

Na atualização, o campo é obrigatório e pode ser utilizado para:

- desativar um usuário;
- reativar um usuário;
- manter o estado atual.

O login permite somente usuários com:

```json
{
  "ativo": true
}
```

## Exclusão lógica

A exclusão não remove o documento fisicamente.

O campo `ativo` é alterado para:

```json
{
  "ativo": false
}
```

Usuários inativos:

- permanecem armazenados;
- continuam aparecendo na consulta geral;
- não conseguem realizar login;
- podem ser reativados pela rota de atualização;
- continuam reservando seus registros.

---

# Cadastrar usuário

## Rota

```http
POST /api/v1/usuarios/
```

## Cabeçalho

```http
Content-Type: application/json
```

## JSON de entrada

```json
{
  "usuario": {
    "registro": 101,
    "nome": "Carlos Silva",
    "email": "carlos@example.com",
    "senha": "Senha@123",
    "role": "Professor"
  }
}
```

Todos os campos apresentados são obrigatórios.

O campo `ativo` não precisa ser enviado. A API define automaticamente o valor `true`.

## Armazenamento da senha

Antes de salvar o usuário, a API transforma a senha em um hash utilizando `bcrypt`.

Representação conceitual no banco:

```json
{
  "registro": 101,
  "nome": "Carlos Silva",
  "email": "carlos@example.com",
  "senha": "$2b$12$...",
  "role": "Professor",
  "ativo": true
}
```

O valor original de `senha` não é armazenado.

## Resposta de sucesso

Código HTTP:

```http
201 Created
```

Resposta atual:

```json
{
  "sucesso": true,
  "mensagem": "Cadastro realizado com sucesso",
  "data": {
    "usuario": {
      "registro": 101,
      "nome": "Carlos Silva",
      "email": "carlos@example.com",
      "role": "Professor",
      "ativo": null
    }
  }
}
```

Atualmente, o campo `ativo` aparece como `null` na resposta do cadastro porque ela é formatada a partir do JSON recebido e o frontend normalmente não envia esse campo.

No banco, o usuário é corretamente armazenado com:

```json
{
  "ativo": true
}
```

A senha não aparece na resposta.

Para consultar a representação armazenada, utilize:

```http
GET /api/v1/usuarios/?registro=101
```

## Possíveis erros

### Chave `usuario` ausente

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
    "mensagem": "O campo 'usuario' é obrigatório!"
  }
}
```

### Campo obrigatório ausente

Exemplo sem o campo `email`:

```json
{
  "usuario": {
    "registro": 101,
    "nome": "Carlos Silva",
    "senha": "Senha@123",
    "role": "Professor"
  }
}
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'email' é obrigatório!"
  }
}
```

### Registro repetido

Código HTTP:

```http
400 Bad Request
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Registro repetido",
  "erro": {
    "mensagem": "O funcionário com o registro 101 já está cadastrado"
  }
}
```

Um usuário inativo também impede a criação de outro usuário com o mesmo registro.

### Registro inválido

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

### Nome inválido

Resposta possível:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Nome do funcionário deve ter ao menos um sobrenome"
  }
}
```

### E-mail inválido

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Email Inválido"
  }
}
```

### Senha muito curta

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Senha deve ter ao menos 6 caracteres"
  }
}
```

### Senha sem letra maiúscula

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Senha deve conter ao menos uma letra maiúscula"
  }
}
```

### Senha sem número

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Senha deve conter ao menos um número"
  }
}
```

### Senha sem caractere especial

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Senha deve conter ao menos um caracter especial"
  }
}
```

### Papel inválido

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Role inválido. Valores permitidos: {'Professor', 'Processo pedagógico'}"
  }
}
```

A ordem dos valores exibidos no conjunto pode variar, mas os papéis permitidos permanecem os mesmos.

---

# Autenticar usuário

## Rota

```http
POST /api/v1/usuarios/login
```

## Cabeçalho

```http
Content-Type: application/json
```

## JSON de entrada

```json
{
  "usuario": {
    "registro": 101,
    "senha": "Senha@123"
  }
}
```

Os dois campos são obrigatórios.

## Funcionamento

A API:

1. procura um usuário ativo com o registro informado;
2. recupera o hash da senha armazenado;
3. compara a senha recebida com o hash por meio do `bcrypt`;
4. retorna os dados públicos do usuário quando as credenciais são válidas.

## Resposta de sucesso

Código HTTP:

```http
200 OK
```

Resposta:

```json
{
  "sucesso": true,
  "mensagem": "Login efetuado com sucesso!",
  "data": {
    "usuario": {
      "registro": 101,
      "nome": "Carlos Silva",
      "email": "carlos@example.com",
      "role": "Professor"
    }
  }
}
```

A resposta não contém:

- senha;
- hash da senha;
- campo `ativo`;
- token JWT.

## Token JWT

Atualmente, nenhum token é gerado.

O frontend recebe somente os dados públicos do usuário autenticado.

Quando o JWT for implementado, a resposta poderá ser ampliada para algo semelhante a:

```json
{
  "sucesso": true,
  "mensagem": "Login efetuado com sucesso!",
  "data": {
    "usuario": {
      "registro": 101,
      "nome": "Carlos Silva",
      "email": "carlos@example.com",
      "role": "Professor"
    },
    "token": "token-jwt"
  }
}
```

Esse formato é apenas uma sugestão futura e ainda não representa a resposta atual.

## Credenciais inválidas

A API utiliza a mesma resposta quando:

- o registro não existe;
- a senha está incorreta;
- o usuário está inativo.

Código HTTP:

```http
401 Unauthorized
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Usuário ou senha inválidos",
  "erro": {
    "mensagem": "Não foi possível realizar autenticação"
  }
}
```

A API não informa qual credencial estava incorreta.

## Registro com tipo inválido

Exemplo:

```json
{
  "usuario": {
    "registro": "101",
    "senha": "Senha@123"
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

## Campo obrigatório ausente

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'senha' é obrigatório!"
  }
}
```

---

# Importar usuários por planilha

## Rota

```http
POST /api/v1/usuarios/excel
```

## Cabeçalho

```http
Content-Type: multipart/form-data
```

## Campo do arquivo

A rota utiliza o primeiro arquivo encontrado na requisição.

Nome recomendado para o campo:

```text
arquivo
```

Exemplo com cURL:

```bash
curl -X POST \
  -F "arquivo=@usuarios.xlsx" \
  http://localhost:8080/api/v1/usuarios/excel
```

## Extensão aceita

O nome do arquivo deve terminar exatamente com:

```text
.xlsx
```

A verificação diferencia letras maiúsculas de minúsculas.

Portanto:

```text
usuarios.xlsx
```

é aceito, enquanto:

```text
usuarios.XLSX
```

é rejeitado.

## Colunas esperadas

A planilha deve possuir as seguintes colunas:

| Coluna | Tipo esperado | Descrição |
|---|---|---|
| `registro` | inteiro | Registro do usuário |
| `nome` | string | Nome completo |
| `email` | string | E-mail |
| `senha` | string | Senha inicial |
| `role` | string | Papel no sistema |

Os nomes devem corresponder exatamente aos utilizados pela API.

## Exemplo da planilha

| registro | nome | email | senha | role |
|---:|---|---|---|---|
| 101 | Carlos Silva | carlos@example.com | Senha@123 | Professor |
| 102 | Marcos Souza | marcos@example.com | Acesso@456 | Processo pedagógico |
| 103 | Roberto Lima | roberto@example.com | MinhaSenha@7 | Professor |

## Validações da importação

Cada linha passa pelas mesmas validações do modelo de usuário:

- registro inteiro;
- nome completo;
- e-mail válido;
- senha válida;
- papel permitido.

Além disso:

- linhas com qualquer valor nulo são ignoradas;
- linhas inválidas são ignoradas;
- registros que já existem no banco são ignorados;
- os demais usuários são reunidos e inseridos no banco;
- a rota não atualiza usuários existentes;
- a rota não informa quais linhas foram ignoradas.

A importação não possui o mesmo comportamento transacional do fluxo de alunos.

Uma linha inválida não impede, por si só, que as outras linhas válidas sejam processadas.

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
    "usuarios inseridos": 3
  }
}
```

O campo `usuarios inseridos` informa quantas linhas válidas e ainda não cadastradas foram preparadas para inserção.

## Nenhum usuário inserido

Quando todas as linhas são inválidas ou possuem registros já cadastrados:

```json
{
  "sucesso": true,
  "mensagem": "Executado com sucesso",
  "data": {
    "usuarios inseridos": 0
  }
}
```

## Arquivo não enviado

Código HTTP:

```http
400 Bad Request
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Arquivo não enviado",
  "erro": "O arquivo excel não foi enviado na requisição"
}
```

## Extensão inválida

Código HTTP:

```http
400 Bad Request
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Formato inválido",
  "erro": "O tipo de arquivo deve ser .xlsx"
}
```

## Coluna ausente ou linha inválida

A implementação atual captura erros encontrados durante a leitura de cada linha e ignora essa linha.

Por isso, uma planilha com colunas ausentes ou dados inválidos pode retornar:

```json
{
  "sucesso": true,
  "mensagem": "Executado com sucesso",
  "data": {
    "usuarios inseridos": 0
  }
}
```

Atualmente, a resposta não apresenta uma lista dos erros encontrados.

## Limitação atual da senha importada

Na implementação atual, a senha da planilha é validada e transformada em hash, mas o documento construído para a importação não inclui o campo `senha`.

Consequentemente, usuários criados por essa importação podem ser armazenados sem senha e não conseguir realizar login.

Esse é um comportamento atual da implementação e deve ser corrigido antes de utilizar a importação de usuários como fluxo definitivo de cadastro.

Enquanto isso, para garantir que o usuário possa realizar login, utilize o cadastro individual:

```http
POST /api/v1/usuarios/
```

---

# Consultar usuários

## Rota

```http
GET /api/v1/usuarios/
```

A rota não exige corpo JSON.

## Consultar todos os usuários

```http
GET /api/v1/usuarios/
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
    "usuarios": [
      {
        "registro": 101,
        "nome": "Carlos Silva",
        "email": "carlos@example.com",
        "role": "Professor",
        "ativo": true
      },
      {
        "registro": 102,
        "nome": "Marcos Souza",
        "email": "marcos@example.com",
        "role": "Processo pedagógico",
        "ativo": false
      }
    ]
  }
}
```

Na resposta:

- o `_id` interno do MongoDB não é retornado;
- a senha não é retornada;
- usuários ativos e inativos podem aparecer;
- o campo `ativo` é retornado.

## Usuários inativos

Diferentemente dos fluxos de disciplinas e provas, a consulta geral de usuários não remove automaticamente os registros inativos.

Para consultar apenas usuários ativos:

```http
GET /api/v1/usuarios/?ativo=true
```

Para consultar apenas usuários inativos:

```http
GET /api/v1/usuarios/?ativo=false
```

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
    "usuarios": []
  }
}
```

---

# Filtros de consulta

## Filtros permitidos

| Parâmetro | Tipo esperado | Descrição |
|---|---|---|
| `registro` | inteiro | Registro do usuário |
| `nome` | string | Nome do usuário |
| `email` | string | E-mail do usuário |
| `role` | string | Papel do usuário |
| `ativo` | booleano | Estado do usuário |

Os filtros realizam correspondência exata com os valores armazenados.

## Consultar por registro

```http
GET /api/v1/usuarios/?registro=101
```

O valor é convertido para número inteiro.

## Consultar por nome

```http
GET /api/v1/usuarios/?nome=Carlos%20Silva
```

Como o nome é armazenado com iniciais maiúsculas, recomenda-se utilizar o mesmo formato na consulta.

## Consultar por e-mail

```http
GET /api/v1/usuarios/?email=carlos@example.com
```

Como o e-mail é armazenado em letras minúsculas, recomenda-se utilizar letras minúsculas na consulta.

## Consultar por papel

```http
GET /api/v1/usuarios/?role=Professor
```

Ou:

```http
GET /api/v1/usuarios/?role=Processo%20pedagógico
```

## Consultar por estado ativo

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
GET /api/v1/usuarios/?ativo=true
```

```http
GET /api/v1/usuarios/?ativo=0
```

## Combinar filtros

```http
GET /api/v1/usuarios/?role=Professor&ativo=true
```

O usuário precisa atender a todos os filtros informados.

## Parâmetro desconhecido

Exemplo:

```http
GET /api/v1/usuarios/?senha=Senha@123
```

Código HTTP:

```http
400 Bad Request
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Parâmetro de pesquisa inválido",
  "erro": "Parâmetro não permitido: senha"
}
```

## Registro inválido no filtro

Exemplo:

```http
GET /api/v1/usuarios/?registro=abc
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Parâmetro de pesquisa inválido",
  "erro": "registro inválido: abc"
}
```

Código HTTP:

```http
400 Bad Request
```

## Booleano inválido

Exemplo:

```http
GET /api/v1/usuarios/?ativo=sim
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Parâmetro de pesquisa inválido",
  "erro": "ativo inválido: sim"
}
```

Código HTTP:

```http
400 Bad Request
```

## Parâmetros vazios

Parâmetros vazios são ignorados.

Exemplo:

```http
GET /api/v1/usuarios/?nome=
```

A requisição possui o mesmo efeito de uma consulta sem esse filtro.

---

# Atualizar usuário

## Rota

```http
PUT /api/v1/usuarios/{registro}
```

Exemplo:

```http
PUT /api/v1/usuarios/101
```

## Cabeçalho

```http
Content-Type: application/json
```

## JSON de entrada

```json
{
  "usuario": {
    "nome": "Carlos Souza",
    "email": "carlos.souza@example.com",
    "role": "Professor",
    "ativo": true
  }
}
```

Todos os campos apresentados são obrigatórios.

O registro é obtido pela URL e não deve ser enviado no corpo.

A atualização não é parcial. Todos os campos devem ser enviados.

## Campos atualizados

A rota atualiza:

- `nome`;
- `email`;
- `role`;
- `ativo`.

A rota não altera:

- `registro`;
- `senha`.

O hash da senha existente é preservado.

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
    "usuario": {
      "registro": 101,
      "nome": "Carlos Souza",
      "email": "carlos.souza@example.com",
      "role": "Professor",
      "ativo": true
    }
  }
}
```

## Desativar pela atualização

```http
PUT /api/v1/usuarios/101
```

```json
{
  "usuario": {
    "nome": "Carlos Souza",
    "email": "carlos.souza@example.com",
    "role": "Professor",
    "ativo": false
  }
}
```

## Reativar usuário

Um usuário excluído logicamente pode ser reativado pela rota de atualização.

```http
PUT /api/v1/usuarios/101
```

```json
{
  "usuario": {
    "nome": "Carlos Souza",
    "email": "carlos.souza@example.com",
    "role": "Professor",
    "ativo": true
  }
}
```

Depois da reativação, o usuário volta a poder realizar login com sua senha anterior.

## Usuário inexistente

Código HTTP:

```http
400 Bad Request
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Usuário não encontrado",
  "erro": {
    "mensagem": "O usuário com o registro 999 não está cadastrado"
  }
}
```

## Campo obrigatório ausente

Exemplo sem `ativo`:

```json
{
  "usuario": {
    "nome": "Carlos Souza",
    "email": "carlos.souza@example.com",
    "role": "Professor"
  }
}
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Erro na validação de dados",
  "erro": {
    "mensagem": "O campo 'ativo' é obrigatório!"
  }
}
```

## Estado ativo inválido

Exemplo:

```json
{
  "usuario": {
    "nome": "Carlos Souza",
    "email": "carlos.souza@example.com",
    "role": "Professor",
    "ativo": "true"
  }
}
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Ativo deve ser booleano"
  }
}
```

No corpo JSON, `ativo` deve ser um booleano real:

```json
{
  "ativo": true
}
```

e não uma string:

```json
{
  "ativo": "true"
}
```

## Registro inválido na URL

A rota utiliza o conversor inteiro do Flask:

```http
PUT /api/v1/usuarios/{registro}
```

Uma URL como:

```http
PUT /api/v1/usuarios/abc
```

não corresponde à rota e normalmente retorna `404 Not Found`.

---

# Alteração de senha

Atualmente, não existe uma rota específica para:

- alterar senha;
- redefinir senha;
- recuperar senha esquecida.

A rota `PUT /api/v1/usuarios/{registro}` não recebe nem atualiza o campo `senha`.

Uma funcionalidade de alteração de senha deverá ser implementada separadamente caso seja necessária.

---

# Excluir usuário

## Rota

```http
DELETE /api/v1/usuarios/{registro}
```

Exemplo:

```http
DELETE /api/v1/usuarios/101
```

A rota não exige corpo JSON.

## Exclusão lógica

A API altera:

```json
{
  "ativo": false
}
```

O documento e o hash da senha permanecem armazenados.

Depois da exclusão:

- o usuário não consegue realizar login;
- o usuário continua aparecendo na consulta geral;
- o registro continua reservado;
- o usuário pode ser reativado pela rota de atualização.

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

## Usuário inexistente ou já inativo

Código HTTP:

```http
404 Not Found
```

Resposta:

```json
{
  "sucesso": false,
  "mensagem": "Não foi possível desativar o usuário",
  "erro": "Não existe usuario com o registro 101"
}
```

A mesma resposta é utilizada quando:

- o registro não existe;
- o usuário já está inativo.

## Registro inválido na URL

A rota aceita somente números inteiros.

Exemplo:

```http
DELETE /api/v1/usuarios/abc
```

Essa URL normalmente retorna `404 Not Found`, pois não corresponde à rota registrada.

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

## Erro de campo obrigatório

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

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Descrição do erro"
  }
}
```

## Erro de autenticação

```json
{
  "sucesso": false,
  "mensagem": "Usuário ou senha inválidos",
  "erro": {
    "mensagem": "Não foi possível realizar autenticação"
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

1. Cadastre os usuários individualmente.
2. Realize o login utilizando o registro e a senha.
3. Armazene os dados públicos retornados conforme a necessidade do frontend.
4. Consulte os usuários ativos ou inativos pelos filtros.
5. Atualize nome, e-mail, papel ou estado quando necessário.
6. Desative logicamente usuários que não devem mais acessar o sistema.
7. Reative usuários pela atualização quando necessário.

A importação por Excel deve ser utilizada somente depois da correção do armazenamento da senha dos usuários importados.

## Exemplo de fluxo completo

### Cadastro

```http
POST /api/v1/usuarios/
```

```json
{
  "usuario": {
    "registro": 101,
    "nome": "Carlos Silva",
    "email": "carlos@example.com",
    "senha": "Senha@123",
    "role": "Professor"
  }
}
```

### Login

```http
POST /api/v1/usuarios/login
```

```json
{
  "usuario": {
    "registro": 101,
    "senha": "Senha@123"
  }
}
```

### Consulta

```http
GET /api/v1/usuarios/?registro=101
```

### Atualização

```http
PUT /api/v1/usuarios/101
```

```json
{
  "usuario": {
    "nome": "Carlos Souza",
    "email": "carlos.souza@example.com",
    "role": "Professor",
    "ativo": true
  }
}
```

### Exclusão lógica

```http
DELETE /api/v1/usuarios/101
```

### Reativação

```http
PUT /api/v1/usuarios/101
```

```json
{
  "usuario": {
    "nome": "Carlos Souza",
    "email": "carlos.souza@example.com",
    "role": "Professor",
    "ativo": true
  }
}
```