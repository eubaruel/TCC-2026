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

## Limites de requisições da API

A API aplica rate limit às rotas `/api/v1/`. Os padrões consideram vários
usuários no mesmo IP, como na rede da escola:

| Escopo | Limite por IP |
| --- | --- |
| Conjunto das rotas da API | 3.000/minuto e 30.000/hora |
| Cada rota comum | 600/minuto |
| Login | 300/minuto, mais 10/minuto por combinação de IP e registro |
| Correção de provas | 120 lotes/minuto |
| Importação de planilhas (`/excel`) | 30/minuto por rota |

Os limites gerais continuam valendo nas rotas com cotas próprias. Cada
requisição de correção conta como um lote, que pode conter até 50 imagens.
Mudar o ID de uma prova na URL não cria uma cota nova para a mesma rota.
Requisições `OPTIONS` de CORS e arquivos fora da API não consomem as cotas.
O registro informado no login serve apenas para separar tentativas, sem
substituir a validação de senha. Os outros limites usam IP, pois a API não
possui uma identidade autenticada por token em cada requisição.

Ao atingir um limite, a API retorna HTTP **429**, JSON no formato habitual
e o cabeçalho `Retry-After` com o número de segundos até uma nova tentativa.
Também expõe `X-RateLimit-Limit`, `X-RateLimit-Remaining` e `X-RateLimit-Reset`
por CORS. O bloqueio termina automaticamente ao expirar a janela.

Os contadores são compartilhados pelo MongoDB de `URI_BD`/`NOME_BD`, em
`rate_limit_contadores` e `rate_limit_janelas`, com índices TTL para limpeza.
Isso mantém as cotas entre processos e reinícios. O usuário do MongoDB
precisa poder criar essas coleções e índices, além de ler e escrever nelas.
Falhas nesse armazenamento retornam HTTP 503, sem desativar a proteção.

As variáveis `RATE_LIMIT_GLOBAL`, `RATE_LIMIT_ROUTE`, `RATE_LIMIT_LOGIN_IP`,
`RATE_LIMIT_LOGIN_REGISTRO`, `RATE_LIMIT_CORRECAO` e `RATE_LIMIT_IMPORTACAO`
permitem ajustar as cotas; os exemplos estão em `backend/.env.example`.
Separe múltiplas janelas com `;`, por exemplo `3000 per minute;30000 per hour`.
Opcionalmente, `RATELIMIT_STORAGE_URI` permite outro armazenamento compatível;
`memory://` é reservado a testes, pois não compartilha contadores entre processos.

Por padrão, o IP é o da conexão e `X-Forwarded-For` é ignorado. Se a API for
publicada atrás de proxy reverso, configure `TRUSTED_PROXY_HOPS` com o número
exato de proxies confiáveis e restrinja o acesso direto à API ao proxy.
Não ative essa opção em uma API acessível diretamente pela internet.
O microserviço de leitura permanece interno; estes limites são da API principal.

Depois de atualizar o projeto, reinicie pelo `INICIAR.cmd`, que instala as
novas dependências automaticamente, ou reinstale `backend/requirements.txt`
e reinicie a API manualmente.

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
