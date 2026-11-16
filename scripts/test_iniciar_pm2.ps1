$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\iniciar_pm2.ps1"
$initializeTools = ${function:Initialize-TccTools}

function Assert-TccTest($Condition, $Message) {
    if (-not $Condition) { throw $Message }
}

$testRoot = Join-Path ([IO.Path]::GetTempPath()) ('tcc-pm2-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path (Join-Path $testRoot 'backend') | Out-Null
Set-Content -LiteralPath (Join-Path $testRoot 'backend\.env') -Value 'URI_BD=mongodb://example.invalid'
Set-Content -LiteralPath (Join-Path $testRoot 'backend\.env.example') -Value 'URI_BD='
$script:RaizTcc = $testRoot
$script:Calls = @()
$script:Processes = @('sistema-correcao', 'frontend', 'api-principal')
$script:FailPrepare = $false

function Initialize-TccTools { return 'python-test.exe' }
function Invoke-TccCommand {
    param([string]$File, [string[]]$CommandArgs)
    $script:Calls += "$File $($CommandArgs -join ' ')"
    if ($script:FailPrepare -and $File -eq 'python-test.exe') { throw 'Falha simulada na preparacao' }
}
function pm2.cmd {
    param([string]$Action)
    Assert-TccTest ($Action -eq 'jlist') 'Comando PM2 inesperado'
    $script:Calls += 'pm2.cmd jlist'
    $global:LASTEXITCODE = 0
    ConvertTo-Json -InputObject @($script:Processes | ForEach-Object { @{ name = $_ } }) -Compress
}

Start-TccPm2
Assert-TccTest ($script:Calls.Count -eq 7) 'Sequencia incompleta'
Assert-TccTest ($script:Calls[0] -match '--preparar') 'Preparacao deve vir primeiro'
Assert-TccTest ($script:Calls[3] -eq 'pm2.cmd delete sistema-correcao') 'Leitor nao excluido'
Assert-TccTest ($script:Calls[4] -eq 'pm2.cmd delete frontend') 'Frontend nao excluido'
Assert-TccTest ($script:Calls[5] -eq 'pm2.cmd delete api-principal') 'API nao excluida'
Assert-TccTest ($script:Calls[6] -match 'pm2.cmd start .*ecosystem.config.js') 'Config nao iniciada'

$script:Calls = @()
$script:Processes = @()
$Reinstalar = $true
Start-TccPm2
Assert-TccTest ($script:Calls.Count -eq 4) 'Primeira execucao nao deve excluir entradas ausentes'
Assert-TccTest ($script:Calls[0] -match '--reinstalar') 'Reinstalacao nao encaminhada'

$script:Calls = @()
$script:FailPrepare = $true
try { Start-TccPm2; throw 'A falha deveria interromper a inicializacao' }
catch { Assert-TccTest ($_.Exception.Message -eq 'Falha simulada na preparacao') 'Erro inesperado' }
Assert-TccTest ($script:Calls.Count -eq 1) 'PM2 foi chamado apos falha na preparacao'

# Outra raiz simula .env ausente sem remover dados de nenhum teste anterior.
$missingRoot = Join-Path $testRoot 'sem-env'
New-Item -ItemType Directory -Path (Join-Path $missingRoot 'backend') | Out-Null
Set-Content -LiteralPath (Join-Path $missingRoot 'backend\.env.example') -Value 'URI_BD='
$script:RaizTcc = $missingRoot
$savedUri = $env:URI_BD
$savedName = $env:NOME_BD
try {
    $env:URI_BD = $null
    $env:NOME_BD = $null
    $script:Calls = @()
    try { Start-TccPm2; throw 'Deveria solicitar configuracao do banco' }
    catch { Assert-TccTest ($_.Exception.Message -like 'Criado backend/.env.*') 'Erro de configuracao inesperado' }
    Assert-TccTest (Test-Path -LiteralPath (Join-Path $missingRoot 'backend\.env')) 'Modelo .env nao copiado'
    Assert-TccTest ($script:Calls.Count -eq 0) 'Servicos foram alterados sem configurar banco'
} finally {
    $env:URI_BD = $savedUri
    $env:NOME_BD = $savedName
}
Write-Host 'PASS: preparacao antes de deletes, primeira execucao, reinstalacao, falhas e .env ausente.'

# Simula uma maquina sem ferramentas, sem executar instaladores reais.
Set-Item Function:Initialize-TccTools $initializeTools
$script:Installed = @()
$script:Pm2Installed = $false
function Update-TccPath {}
function Get-TccPython {
    if ($script:Installed -contains 'Python.Python.3.13') { return 'python-test.exe' }
}
function Get-Command {
    param($Name, $ErrorAction)
    if ($Name -eq 'node.exe' -and $script:Installed -contains 'OpenJS.NodeJS.LTS') {
        return [pscustomobject]@{ Source = 'node-test.exe' }
    }
    if ($Name -eq 'npm.cmd' -and $script:Installed -contains 'OpenJS.NodeJS.LTS') {
        return [pscustomobject]@{ Source = 'npm.cmd' }
    }
    if ($Name -eq 'pm2.cmd' -and $script:Pm2Installed) {
        return [pscustomobject]@{ Source = 'pm2.cmd' }
    }
}
function node-test.exe { $global:LASTEXITCODE = 0 }
function npm.cmd { $global:LASTEXITCODE = 0; return $testRoot }
function Test-Path {
    param($LiteralPath)
    if ($LiteralPath -like '*System32\*.dll') {
        return $script:Installed -contains 'Microsoft.VCRedist.2015+.x64'
    }
    Microsoft.PowerShell.Management\Test-Path -LiteralPath $LiteralPath
}
function Install-TccPackage { param($Id); $script:Installed += $Id }
function Invoke-TccCommand {
    param([string]$File, [string[]]$CommandArgs)
    Assert-TccTest ($File -eq 'npm.cmd' -and ($CommandArgs -join ' ') -eq 'install --global pm2') 'Instalacao npm inesperada'
    $script:Pm2Installed = $true
}
$result = Initialize-TccTools
Assert-TccTest ($result -eq 'python-test.exe') 'O retorno deve conter somente o interpretador'
Assert-TccTest ($script:Installed.Count -eq 3 -and $script:Pm2Installed) 'Ferramentas ausentes nao instaladas'
$result = Initialize-TccTools
Assert-TccTest ($script:Installed.Count -eq 3) 'Ferramentas existentes foram reinstaladas'
Write-Host 'PASS: instalacao simulada de Python, Node/npm, PM2, VC++ e reaproveitamento das ferramentas.'
