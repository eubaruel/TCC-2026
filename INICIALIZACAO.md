# Inicialização local

Versões instaladas nesta máquina: Python 3.13.13 e Node.js 24.21.0.
O backend utiliza um ambiente Python local em `.venv-correcao`, que deve ser
criado antes da primeira inicialização. A resolução das dependências foi
verificada para Python 3.13; a execução completa depende da instalação dos
pacotes e da configuração do MongoDB.

## Inicializar tudo com um arquivo (Windows)

Dê um duplo clique em `INICIAR.cmd`, na raiz do projeto, ou execute:

```powershell
.\INICIAR.cmd
```

O arquivo prepara os dois ambientes Python e instala as dependências do
frontend na primeira execução, ou quando os arquivos de dependências mudarem.
Depois inicia o leitor de gabaritos, a API e o frontend, aguarda os serviços
ficarem prontos e abre `http://localhost:8081` no navegador.

É necessário ter Python e Node.js com npm instalados e configurar `URI_BD`
e `NOME_BD` em `backend/.env` (ou no ambiente), como explicado abaixo.
O MongoDB configurado precisa estar acessível; o script não instala um banco.
A instalação das dependências precisa de internet.

Mantenha a janela aberta e pressione **Ctrl+C** nela para encerrar os três
serviços. Se uma porta estiver ocupada, o inicializador avisa antes de iniciar.
Os logs ficam em `backend/.venv-correcao/logs-inicializacao/`, separados
por execução e serviço.

Opções disponíveis:

- `.\INICIAR.cmd --verificar`: confere caminhos, configuração e portas sem
  instalar dependências nem iniciar serviços. Requer os ambientes já criados
  e não testa a conexão de rede com o MongoDB.
- `.\INICIAR.cmd --reinstalar`: executa novamente a instalação das dependências.
- `.\INICIAR.cmd --sem-navegador`: inicia tudo sem abrir o navegador.

As instruções a seguir permitem iniciar cada serviço manualmente.

## Backend (PowerShell, dentro de backend)

Se o ambiente não existir, crie-o com o Python instalado no computador:

```powershell
python --version
python -m venv .venv-correcao
```

Não é preciso especificar a versão no comando de criação: a venv utiliza o
interpretador associado ao comando `python` (nesta máquina, Python 3.13.13).
Um ambiente já existente mantém a versão com a qual foi criado.

Para ativar a venv no PowerShell e executar o backend:

```powershell
.\.venv-correcao\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Alternativamente, execute diretamente o Python da venv, sem ativá-la. Esta
opção também funciona se a política do PowerShell bloquear `Activate.ps1`:

```powershell
.\.venv-correcao\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-correcao\Scripts\python.exe app.py
```

Antes de iniciar, configure em `backend/.env` as variáveis `URI_BD` e
`NOME_BD`; `PORTA` é opcional. Também é possível defini-las como variáveis
de ambiente. Não inclua credenciais do banco no controle de versão.
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

## Microserviço de correção (outro terminal, dentro de backend)

O microserviço `sistema-correcao` usa um ambiente separado, `.venv-leitor`,
para não misturar as dependências de processamento de imagens com as da API.
Esse ambiente está ignorado pelo Git e não deve ser enviado nos commits.

Na primeira execução, crie o ambiente e instale as dependências:

```powershell
python -m venv .venv-leitor
.\.venv-leitor\Scripts\python.exe -m pip install -r sistema-correcao\requirements.txt
```

Para iniciar o leitor, partindo da pasta `backend`:

```powershell
Set-Location .\sistema-correcao
..\.venv-leitor\Scripts\python.exe -m flask --app app --no-debug run --host 127.0.0.1 --port 5000 --no-reload
```

Verifique `http://127.0.0.1:5000/health`: a resposta esperada é
`{"status": "ok"}`. A API principal utiliza esse endereço por padrão,
ou o endereço definido em `CORRECAO_URL`. O leitor não é necessário para
testar o login, mas deve permanecer em execução para a correção de provas.
