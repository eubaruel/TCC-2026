# Inicialização local

Ambiente verificado: Python 3.12 e Node.js 24.21.0.
O backend possui um ambiente Python local em `.venv-correcao`.

## Backend (PowerShell, dentro de backend)

```powershell
.\.venv-correcao\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-correcao\Scripts\python.exe app.py
```

Se o ambiente não existir, crie-o com uma instalação Python 3.12:

```powershell
py -3.12 -m venv .venv-correcao
```

Não é necessário ativar o ambiente para executar os comandos acima.
A configuração permanece no `.env`: `URI_BD`, `NOME_BD` e `PORTA`.
A API utiliza a porta 8080 por padrão. O MongoDB configurado precisa estar
acessível pela rede, inclusive sua resolução DNS.

O `app.py` chama a criação das contas de desenvolvimento antes de iniciar
o Flask. Registros: 1 (Professor) e 2 (Processo pedagógico), senha `Teste123!`.
Contas existentes não são modificadas. Remova essa chamada antes de produção.

## Frontend (outro terminal, dentro de frontend)

```powershell
npm.cmd ci
npm.cmd run serve
```

Usar `npm.cmd` evita depender da política de execução dos scripts PowerShell.
O frontend fica em `http://localhost:8081` e chama a API em
`http://localhost:8080/api/v1`, salvo configuração explícita de
`VUE_APP_API_BASE_URL`.

Para verificar a compilação de produção:

```powershell
npm.cmd run build
```

O núcleo, preset, plugin e runtime do Babel utilizam a série 7.
O antigo `cache-loader` não é necessário para o Vue CLI 5 utilizado aqui.
O `package-lock.json` foi atualizado e deve ser mantido no controle de versão.

O microserviço `sistema-correcao` é separado e não foi alterado. Ele não é
necessário para testar o login.
