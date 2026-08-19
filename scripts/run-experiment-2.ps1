$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LocalPackages = Join-Path $ProjectRoot ".local-packages"
$Source = Join-Path $ProjectRoot "src"
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$ResultDirectory = Join-Path $ProjectRoot "reports\experiment-2\$Timestamp"
$JUnitXml = Join-Path $ResultDirectory "junit-ci-rehearsal.xml"
$DistDirectory = Join-Path $ProjectRoot "dist"

if (-not (Test-Path (Join-Path $LocalPackages "pytest"))) {
    throw "Local pytest not found. Run scripts/setup-local.ps1 first."
}
if (-not (Test-Path (Join-Path $LocalPackages "build"))) {
    throw "Local build package not found. Run scripts/setup-local.ps1 again."
}

New-Item -ItemType Directory -Force -Path $ResultDirectory | Out-Null
$env:PYTHONPATH = "$LocalPackages;$Source;$ProjectRoot"
$env:PYTHONUTF8 = "1"
$env:PYTHONDONTWRITEBYTECODE = "1"

Push-Location $ProjectRoot
try {
    @(
        "Experiment 2 executed at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')"
        "Operating system: $([System.Environment]::OSVersion.VersionString)"
        "Python: $(python --version 2>&1)"
        "pytest: $(python -m pytest --version 2>&1)"
        "build: $(python -m build --version 2>&1)"
        "Workflow: .github/workflows/ci.yml"
        "Cloud status: not executed; no GitHub remote is configured"
    ) | Set-Content -Encoding UTF8 (Join-Path $ResultDirectory "environment.txt")

    python -m pytest -v "--junitxml=$JUnitXml" 2>&1 |
        Tee-Object -FilePath (Join-Path $ResultDirectory "test.log")
    $TestExitCode = $LASTEXITCODE

    cmd.exe /d /c "python -m build --no-isolation 2>&1" |
        Tee-Object -FilePath (Join-Path $ResultDirectory "build.log")
    $BuildExitCode = $LASTEXITCODE

    python .\scripts\verify_distribution.py $DistDirectory 2>&1 |
        Tee-Object -FilePath (Join-Path $ResultDirectory "distribution-check.log")
    $DistributionExitCode = $LASTEXITCODE

    $ArtifactLines = @()
    Get-ChildItem -LiteralPath $DistDirectory -File | Sort-Object Name | ForEach-Object {
        $Hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash
        $ArtifactLines += "$($_.Name) | $($_.Length) bytes | SHA256=$Hash"
    }
    $ArtifactLines | Set-Content -Encoding UTF8 (Join-Path $ResultDirectory "artifacts.txt")

    if (Test-Path $JUnitXml) {
        [xml]$JUnit = Get-Content -Raw -LiteralPath $JUnitXml
        $Suite = $JUnit.testsuites.testsuite
        $JUnitSummary = "tests=$($Suite.tests), failures=$($Suite.failures), errors=$($Suite.errors), skipped=$($Suite.skipped), time=$($Suite.time)s"
    } else {
        $JUnitSummary = "JUnit XML not generated"
    }

    @(
        "Experiment 2 local CI rehearsal summary"
        "Result directory: $ResultDirectory"
        "Test exit code: $TestExitCode"
        "JUnit: $JUnitSummary"
        "Build exit code: $BuildExitCode"
        "Distribution verification exit code: $DistributionExitCode"
        "Cloud run: pending because no GitHub remote/account connection is available"
        "Verdict: local CI rehearsal passes only when all three exit codes are zero."
    ) | Set-Content -Encoding UTF8 (Join-Path $ResultDirectory "summary.txt")

    Set-Content -Encoding UTF8 (Join-Path $ProjectRoot "reports\experiment-2\LATEST.txt") $ResultDirectory

    if ($TestExitCode -ne 0 -or $BuildExitCode -ne 0 -or $DistributionExitCode -ne 0) {
        throw "Experiment 2 local rehearsal failed. Inspect $ResultDirectory"
    }
    Write-Host "Experiment 2 local rehearsal passed. Evidence: $ResultDirectory"
}
finally {
    Pop-Location
}
