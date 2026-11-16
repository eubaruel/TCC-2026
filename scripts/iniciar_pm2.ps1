param([switch]$Reinstalar)

$ErrorActionPreference = 'Stop'
$script:RaizTcc = Split-Path -Parent $PSScriptRoot

function Update-TccPath {
    # Mantem o PATH recebido e inclui ferramentas instaladas nesta execucao.
    $paths = @($env:Path,
        [Environment]::GetEnvironmentVariable('Path', 'Machine'),
        [Environment]::GetEnvironmentVariable('Path', 'User'),
        (Join-Path $env:APPDATA 'npm'),
        (Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps'),
        (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313'),
        (Join-Path $env:ProgramFiles 'Python313'),
        (Join-Path $env:ProgramFiles 'nodejs'))
    $env:Path = ($paths | Where-Object { $_ } | Select-Object -Unique) -join ';'
}

function Invoke-TccCommand {
    param([string]$File, [string[]]$CommandArgs)
    & $File @CommandArgs | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Falha em $File (codigo $LASTEXITCODE). A inicializacao foi interrompida."
    }
}

function Get-TccPython {
    $candidates = @(
        (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313\python.exe'),
        (Join-Path $env:ProgramFiles 'Python313\python.exe'))
    $command = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($command -and $command.Source -notmatch 'WindowsApps') { $candidates += $command.Source }
    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        if (Test-Path -LiteralPath $candidate) {
            & $candidate -c 'import sys; sys.exit(0 if sys.version_info[:2] == (3, 13) and sys.maxsize > 2**32 else 1)' 2>$null
            if ($LASTEXITCODE -eq 0) { return $candidate }
        }
    }
}

function Install-TccPackage {
    param([string]$Id)
    if (-not (Get-Command winget.exe -ErrorAction SilentlyContinue)) {
        Write-Host 'Preparando o WinGet pelo modulo oficial da Microsoft...'
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Install-PackageProvider -Name NuGet -Scope CurrentUser -Force | Out-Null
        Install-Module -Name Microsoft.WinGet.Client -Scope CurrentUser -Force -Repository PSGallery
        Import-Module Microsoft.WinGet.Client
        Repair-WinGetPackageManager -Force -Latest | Out-Host
        Update-TccPath
    }
    Write-Host "Instalando $Id... Aceite a elevacao do Windows se solicitada."
    Invoke-TccCommand 'winget.exe' @('install', '--id', $Id, '--exact', '--source', 'winget',
        '--silent', '--accept-package-agreements', '--accept-source-agreements')
    Update-TccPath
}

function Initialize-TccTools {
    if (-not [Environment]::Is64BitOperatingSystem) { throw 'Use Windows 10/11 de 64 bits.' }
    Update-TccPath
    $python = Get-TccPython
    if (-not $python) {
        Install-TccPackage 'Python.Python.3.13'
        $python = Get-TccPython
    }
    if (-not $python) { throw 'Python 3.13 nao encontrado apos a instalacao. Reinicie o terminal e tente novamente.' }
    $node = Get-Command node.exe -ErrorAction SilentlyContinue
    $nodeOk = $false
    if ($node) {
        & $node.Source -e 'process.exit(Number(process.versions.node.split(String.fromCharCode(46))[0]) >= 22 ? 0 : 1)'
        $nodeOk = $LASTEXITCODE -eq 0
    }
    if (-not $nodeOk -or -not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
        Install-TccPackage 'OpenJS.NodeJS.LTS'
    }
    if (-not (Get-Command node.exe -ErrorAction SilentlyContinue) -or
        -not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
        throw 'Node.js/npm nao encontrados apos a instalacao. Reinicie o terminal e tente novamente.'
    }
    if (-not (Get-Command pm2.cmd -ErrorAction SilentlyContinue)) {
        Write-Host 'Instalando PM2 com npm...'
        Invoke-TccCommand 'npm.cmd' @('install', '--global', 'pm2')
        # Respeita tambem prefixos npm personalizados.
        $prefix = & npm.cmd prefix --global
        if ($LASTEXITCODE -ne 0) { throw 'Nao foi possivel localizar o diretorio do PM2.' }
        $env:Path = "$prefix;$env:Path"
    }
    if (-not (Get-Command pm2.cmd -ErrorAction SilentlyContinue)) { throw 'PM2 nao encontrado apos a instalacao.' }
    $runtimeFiles = @('vcruntime140.dll', 'vcruntime140_1.dll', 'msvcp140.dll')
    if ($runtimeFiles | Where-Object { -not (Test-Path -LiteralPath (Join-Path $env:SystemRoot "System32\$_")) }) {
        Install-TccPackage 'Microsoft.VCRedist.2015+.x64'
    }
    return $python
}

function Start-TccPm2 {
    Push-Location -LiteralPath $script:RaizTcc
    try {
        # Ferramentas e dependencias sao preparadas antes de interromper os servicos.
        $python = Initialize-TccTools
        $envFile = Join-Path $script:RaizTcc 'backend\.env'
        if (-not (Test-Path -LiteralPath $envFile) -and
            (-not $env:URI_BD -or -not $env:NOME_BD)) {
            Copy-Item -LiteralPath (Join-Path $script:RaizTcc 'backend\.env.example') -Destination $envFile
            throw 'Criado backend/.env. Configure URI_BD e NOME_BD do MongoDB remoto e execute INICIAR_PM2.cmd novamente.'
        }
        $prepareArgs = @('-X', 'utf8', '-x', (Join-Path $script:RaizTcc 'INICIAR.cmd'), '--preparar')
        if ($Reinstalar) { $prepareArgs += '--reinstalar' }
        Invoke-TccCommand $python $prepareArgs
        $env:PYTHONUNBUFFERED = '1'
        $env:PYTHONUTF8 = '1'
        # A consulta falha antes dos deletes se o daemon estiver inacessivel.
        Invoke-TccCommand 'pm2.cmd' @('ping')
        $raw = & pm2.cmd jlist
        if ($LASTEXITCODE -ne 0) { throw 'Nao foi possivel acessar o PM2. Nenhum servico foi excluido.' }
        $processes = ($raw -join "`n") | ConvertFrom-Json
        foreach ($name in @('sistema-correcao', 'frontend', 'api-principal')) {
            if ($processes | Where-Object { $_.name -eq $name }) {
                Invoke-TccCommand 'pm2.cmd' @('delete', $name)
            }
        }
        Invoke-TccCommand 'pm2.cmd' @('start', (Join-Path $script:RaizTcc 'ecosystem.config.js'))
        Write-Host 'Servicos enviados ao PM2. Consulte pm2 status e pm2 logs para acompanhar a inicializacao.'
    } finally {
        Pop-Location
    }
}

# Permite carregar as funcoes em testes sem executar instalacoes.
if ($MyInvocation.InvocationName -ne '.') {
    try { Start-TccPm2; exit 0 }
    catch { Write-Host "[ERRO] $($_.Exception.Message)" -ForegroundColor Red; exit 1 }
}
