param(
    [switch]$Offline
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LocalPackages = Join-Path $ProjectRoot ".local-packages"
$Source = Join-Path $ProjectRoot "src"
$ReportDirectory = Join-Path $ProjectRoot "reports"

if (-not (Test-Path (Join-Path $LocalPackages "pytest"))) {
    throw "未找到本地 pytest，请先运行 ./scripts/setup-local.ps1"
}

New-Item -ItemType Directory -Force -Path $ReportDirectory | Out-Null
$env:PYTHONPATH = "$LocalPackages;$Source"

$PytestArguments = @("-m", "pytest", "--junitxml=$ReportDirectory/junit.xml")
if ($Offline) {
    $PytestArguments += @("-m", "not network")
}

Push-Location $ProjectRoot
try {
    python @PytestArguments
    $TestExitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}

exit $TestExitCode
