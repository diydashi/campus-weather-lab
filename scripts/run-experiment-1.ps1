$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LocalPackages = Join-Path $ProjectRoot ".local-packages"
$Source = Join-Path $ProjectRoot "src"
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$ResultDirectory = Join-Path $ProjectRoot "reports\experiment-1\$Timestamp"
$OfflineXml = Join-Path $ResultDirectory "junit-offline.xml"
$NetworkXml = Join-Path $ResultDirectory "junit-network.xml"

if (-not (Test-Path (Join-Path $LocalPackages "pytest"))) {
    throw "Local pytest not found. Run scripts/setup-local.ps1 first."
}

New-Item -ItemType Directory -Force -Path $ResultDirectory | Out-Null
$env:PYTHONPATH = "$LocalPackages;$Source"
$env:PYTHONUTF8 = "1"
$env:PYTHONDONTWRITEBYTECODE = "1"

function Get-JunitSummary([string]$Path) {
    if (-not (Test-Path $Path)) {
        return "JUnit XML not generated"
    }
    [xml]$Document = Get-Content -Raw -LiteralPath $Path
    $Suite = $Document.testsuites.testsuite
    return "tests=$($Suite.tests), failures=$($Suite.failures), errors=$($Suite.errors), skipped=$($Suite.skipped), time=$($Suite.time)s"
}

Push-Location $ProjectRoot
try {
    @(
        "Experiment 1 executed at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')"
        "Operating system: $([System.Environment]::OSVersion.VersionString)"
        "Python: $(python --version 2>&1)"
        "pytest: $(python -m pytest --version 2>&1)"
        "Project root: $ProjectRoot"
    ) | Set-Content -Encoding UTF8 (Join-Path $ResultDirectory "environment.txt")

    python -m pytest -m "not network" -v "--junitxml=$OfflineXml" 2>&1 |
        Tee-Object -FilePath (Join-Path $ResultDirectory "offline-test.log")
    $OfflineExitCode = $LASTEXITCODE

    python -m pytest -m "network" -v "--junitxml=$NetworkXml" 2>&1 |
        Tee-Object -FilePath (Join-Path $ResultDirectory "network-test.log")
    $NetworkExitCode = $LASTEXITCODE

    $SampleExitCode = 1
    if ($NetworkExitCode -eq 0) {
        python .\scripts\capture_api_sample.py (Join-Path $ResultDirectory "api-sample.json")
        $SampleExitCode = $LASTEXITCODE
    }

    $OfflineSummary = Get-JunitSummary $OfflineXml
    $NetworkSummary = Get-JunitSummary $NetworkXml

    @(
        "Experiment 1 test summary"
        "Result directory: $ResultDirectory"
        "Offline test exit code: $OfflineExitCode"
        "Offline JUnit: $OfflineSummary"
        "Live API test exit code: $NetworkExitCode"
        "Live API JUnit: $NetworkSummary"
        "API sample exit code: $SampleExitCode"
        "Verdict: all three exit codes must be zero."
    ) | Set-Content -Encoding UTF8 (Join-Path $ResultDirectory "summary.txt")

    Set-Content -Encoding UTF8 (Join-Path $ProjectRoot "reports\experiment-1\LATEST.txt") $ResultDirectory

    if ($OfflineExitCode -ne 0 -or $NetworkExitCode -ne 0 -or $SampleExitCode -ne 0) {
        throw "Experiment 1 did not fully pass. Inspect $ResultDirectory"
    }

    Write-Host "Experiment 1 passed. Evidence saved to: $ResultDirectory"
}
finally {
    Pop-Location
}
