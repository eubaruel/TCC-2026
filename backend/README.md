# Documentação dos Fluxos da API

Documentação das rotas da API do sistema de banco de questões e criação de provas.

O sistema permite o gerenciamento de usuários, alunos, disciplinas, questões e provas. A integração com o sistema de correção automatizada será realizada posteriormente.

## Tecnologias

- Python
- Flask
- MongoDB
- API REST
- JSON

## Endereço-base

Durante o desenvolvimento local, a API utiliza:

```text
http://localhost:8080/api/v1
```

As rotas apresentadas nos documentos dos fluxos devem ser adicionadas depois desse endereço.

Exemplo:

```text
http://localhost:8080/api/v1/questoes/
```

## Fluxos disponíveis

| Fluxo | Endereço-base | Documentação |
|---|---|---|
| Questões | `/api/v1/questoes` | [Documentação de Questões](./questoes/README.md) |
| Provas | `/api/v1/provas` | [Documentação de Provas](./provas/README.md) |
| Usuários | `/api/v1/usuarios` | [Documentação de Usuários](./usuarios/README.md) |
| Disciplinas | `/api/v1/disciplinas` | [Documentação de Disciplinas](./disciplinas/README.md) |
| Alunos | `/api/v1/alunos` | [Documentação de Alunos](./alunos/README.md) |

## Métodos HTTP utilizados

| Método | Finalidade |
|---|---|
| `GET` | Consultar recursos |
| `POST` | Cadastrar recursos |
| `PUT` | Atualizar recursos existentes |
| `PATCH` | Atualizar parcialmente um recurso |
| `DELETE` | Desativar ou excluir logicamente um recurso |

A disponibilidade de cada método depende do fluxo documentado.

## Formato das requisições

As requisições que enviam dados devem utilizar o cabeçalho:

```http
Content-Type: application/json
```

Exemplo:

```http
POST /api/v1/questoes/
Content-Type: application/json
```

O corpo deve ser enviado em formato JSON:

```json
{
  "questao": {
    "campo": "valor"
  }
}
```

Cada fluxo possui uma chave principal correspondente ao recurso:

| Fluxo | Chave principal |
|---|---|
| Questões | `questao` |
| Provas | `prova` |
| Usuários | `usuario` |
| Disciplinas | `disciplina` |
| Alunos | `aluno` |

## Formato das respostas de sucesso

As respostas bem-sucedidas seguem esta estrutura:

```json
{
  "sucesso": true,
  "mensagem": "Operação realizada com sucesso",
  "data": {}
}
```

O conteúdo de `data` varia conforme a rota.

Exemplo de cadastro:

```json
{
  "sucesso": true,
  "mensagem": "Cadastro realizado com sucesso",
  "data": {
    "recurso": {}
  }
}
```

Exemplo de consulta:

```json
{
  "sucesso": true,
  "mensagem": "Executado com sucesso",
  "data": {
    "recursos": []
  }
}
```

Algumas operações podem retornar `data` como `null` quando não existe conteúdo adicional para enviar:

```json
{
  "sucesso": true,
  "mensagem": "Excluído com sucesso",
  "data": null
}
```

## Formato das respostas de erro

Erros de validação ou regras de negócio seguem esta estrutura:

```json
{
  "sucesso": false,
  "mensagem": "Dados inválidos",
  "erro": {
    "detalhes": "Descrição do problema encontrado"
  }
}
```

A estrutura interna de `erro` pode variar conforme o tipo de problema:

```json
{
  "sucesso": false,
  "mensagem": "Questão não encontrada",
  "erro": {
    "mensagem": "Uma ou mais questões não existem ou estão inativas"
  }
}
```

Erros internos utilizam uma mensagem genérica:

```json
{
  "sucesso": false,
  "mensagem": "Ocorreu um erro interno no servidor",
  "erro": {
    "codigo": "INTERNAL_ERROR"
  }
}
```

## Códigos HTTP utilizados

| Código | Significado |
|---|---|
| `200 OK` | Consulta, atualização ou exclusão realizada |
| `201 Created` | Recurso cadastrado |
| `400 Bad Request` | Dados inválidos ou regra de negócio violada |
| `404 Not Found` | Rota ou recurso não encontrado |
| `500 Internal Server Error` | Erro interno inesperado |

## Identificadores

Os recursos armazenados no MongoDB normalmente possuem um identificador no campo:

```json
{
  "_id": "64b000000000000000000001"
}
```

Esse identificador deve ser utilizado nas rotas de atualização, exclusão e associação entre recursos.

Exemplo:

```http
PUT /api/v1/questoes/64b000000000000000000001
```

As alternativas das questões objetivas possuem identificadores próprios:

```json
{
  "id": "uuid-da-alternativa",
  "texto": "Texto da alternativa"
}
```

O campo `alternativa_correta` armazena o ID de uma das alternativas:

```json
{
  "alternativa_correta": "uuid-da-alternativa"
}
```

## Parâmetros de consulta

Algumas rotas `GET` aceitam filtros por query parameters.

Exemplo:

```http
GET /api/v1/questoes/?tipo_questao=Objetiva&dificuldade=Médio
```

Somente os parâmetros documentados em cada fluxo são permitidos. Um parâmetro desconhecido resulta em HTTP `400`.

## Exclusão lógica

Alguns recursos utilizam exclusão lógica.

Nesses casos, o documento não é removido fisicamente do MongoDB. O campo interno `ativo` é alterado:

```json
{
  "ativo": false
}
```

Recursos inativos deixam de aparecer nas consultas normais e não podem ser utilizados em novos relacionamentos.

O campo interno `ativo` pode ser omitido das respostas da API.

## Autenticação

A autenticação por token JWT ainda não está implementada.

As regras atuais de login e acesso estão descritas no fluxo de usuários:

[Documentação de Usuários](./usuarios/README.md)

## Ordem recomendada de leitura

Para compreender a utilização completa da API, recomenda-se esta ordem:

1. [Usuários](./api/docs/Documentações%20de%20rotas/Usuários.md)
2. [Disciplinas](./api/docs/Documentações%20de%20rotas/Disciplinas.md)
3. [Alunos](./api/docs/Documentações%20de%20rotas/Alunos.md)
4. [Questões](./api/docs/Documentações%20de%20rotas/Questões.md)
5. [Provas](./api/docs/Documentações%20de%20rotas/Provas.md)

## Observações

- Todos os exemplos utilizam dados fictícios.
- Os IDs exibidos são apenas exemplos.
- Os nomes dos campos devem ser enviados exatamente como documentados.
- Valores de texto podem passar por normalização antes de serem armazenados.
- As validações específicas estão descritas no README de cada fluxo.
- O sistema de correção automatizada não faz parte desta documentação.