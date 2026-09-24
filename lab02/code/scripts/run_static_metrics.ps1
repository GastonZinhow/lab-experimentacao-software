param(
    [string]$SourcePath = "src/main/java",
    [string]$OutputDir = "data/processed",
    [string]$CkJarPath = "",
    [string]$PmdBinPath = "",
    [int]$MinimumTokens = 50,
    [string]$RunId = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RequiredPath([string]$Path, [string]$Description) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Description nao encontrado: $Path"
    }

    return (Resolve-Path -LiteralPath $Path).Path
}

function Add-CsvRow($CsvPath, $RunId, $SourcePath, $Tool, $OutputPath, $Status, $ExitCode, $Notes) {
    $line = """{0}"",""{1}"",""{2}"",""{3}"",""{4}"",""{5}"",{6},""{7}""" -f `
        $RunId, `
        (Get-Date).ToString("s"), `
        $SourcePath, `
        $Tool, `
        $OutputPath, `
        $Status, `
        $ExitCode, `
        ($Notes -replace '"', "'")

    Add-Content -LiteralPath $CsvPath -Value $line -Encoding UTF8
}

function Invoke-NativeCommand($CommandLine, $LogPath) {
    & cmd.exe /c "$CommandLine > `"$LogPath`" 2>&1"
    return $LASTEXITCODE
}

function Invoke-NativeCommandWithSeparateOutput($CommandLine, $OutputPath, $LogPath) {
    & cmd.exe /c "$CommandLine > `"$OutputPath`" 2> `"$LogPath`""
    return $LASTEXITCODE
}

$root = (Resolve-Path -LiteralPath ".").Path
$source = Resolve-RequiredPath $SourcePath "Diretorio de codigo fonte"
$processed = Join-Path $root $OutputDir
New-Item -ItemType Directory -Force -Path $processed | Out-Null

$runName = if ($RunId) { $RunId } else { "run-" + (Get-Date).ToString("yyyyMMdd-HHmmss") }
$staticMetricsCsv = Join-Path $processed "static_metrics_runs.csv"
if (-not (Test-Path -LiteralPath $staticMetricsCsv)) {
    "run_id,collected_at,source_path,tool,output_path,status,exit_code,notes" | Set-Content -LiteralPath $staticMetricsCsv -Encoding UTF8
}

if (-not (Get-Command "java" -ErrorAction SilentlyContinue)) {
    throw "Comando 'java' nao encontrado. Instale/configure o JDK antes de rodar CK."
}

if ($CkJarPath -and (Test-Path -LiteralPath $CkJarPath)) {
    $ckJar = (Resolve-Path -LiteralPath $CkJarPath).Path
    $ckOutput = Join-Path $processed "ck\$runName"
    $ckLog = Join-Path $processed "ck-$runName.log"
    New-Item -ItemType Directory -Force -Path $ckOutput | Out-Null
    # O CK concatena o nome do CSV direto no caminho de saida, entao a barra final e obrigatoria
    $exitCode = Invoke-NativeCommand "java -jar `"$ckJar`" `"$source`" false 0 false `"$ckOutput/`"" $ckLog
    $status = if ($exitCode -eq 0) { "ok" } else { "failed" }
    $notes = if ($exitCode -eq 0) { "CK executado" } else { "CK falhou; veja o log" }
    Add-CsvRow $staticMetricsCsv $runName $source "CK" $ckOutput $status $exitCode $notes
    Write-Host "CK: saida em $ckOutput"
}
else {
    Add-CsvRow $staticMetricsCsv $runName $source "CK" "" "skipped" 0 "Informe -CkJarPath para executar CK"
    Write-Warning "CK nao executado. Informe -CkJarPath apontando para ck.jar."
}

if ($PmdBinPath -and (Test-Path -LiteralPath $PmdBinPath)) {
    $pmdBin = (Resolve-Path -LiteralPath $PmdBinPath).Path
    $cpdDir = Join-Path $processed "cpd"
    New-Item -ItemType Directory -Force -Path $cpdDir | Out-Null
    $cpdOutput = Join-Path $cpdDir "cpd-$runName.xml"
    $cpdLog = Join-Path $cpdDir "cpd-$runName.log"
    $exitCode = Invoke-NativeCommandWithSeparateOutput "`"$pmdBin`" cpd --minimum-tokens $MinimumTokens --dir `"$source`" --language java --format xml" $cpdOutput $cpdLog
    $status = if ($exitCode -eq 0) { "ok" } else { "failed" }
    $notes = if ($exitCode -eq 0) { "PMD CPD executado" } else { "PMD CPD encontrou duplicacao ou falhou; veja XML/log" }
    Add-CsvRow $staticMetricsCsv $runName $source "PMD_CPD" $cpdOutput $status $exitCode $notes
    Write-Host "PMD CPD: saida em $cpdOutput"
}
else {
    Add-CsvRow $staticMetricsCsv $runName $source "PMD_CPD" "" "skipped" 0 "Informe -PmdBinPath para executar PMD CPD"
    Write-Warning "PMD CPD nao executado. Informe -PmdBinPath apontando para pmd.bat."
}

Write-Host "Resumo salvo em $staticMetricsCsv"
