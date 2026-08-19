$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LocalPackages = Join-Path $ProjectRoot ".local-packages"
$Source = Join-Path $ProjectRoot "src"
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$ResultDirectory = Join-Path $ProjectRoot "reports\experiment-3\$Timestamp"
$Iterations = 10000
$BaselineJson = Join-Path $ResultDirectory "baseline-metrics.json"
$OptimizedJson = Join-Path $ResultDirectory "optimized-metrics.json"
$ComparisonJson = Join-Path $ResultDirectory "comparison.json"
$BaselineProfile = Join-Path $ResultDirectory "cpu-baseline.prof"
$OptimizedProfile = Join-Path $ResultDirectory "cpu-optimized.prof"

New-Item -ItemType Directory -Force -Path $ResultDirectory | Out-Null
$env:PYTHONPATH = "$LocalPackages;$Source;$ProjectRoot"
$env:PYTHONUTF8 = "1"
$env:PYTHONDONTWRITEBYTECODE = "1"

Push-Location $ProjectRoot
try {
    @(
        "Experiment 3 executed at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')"
        "Operating system: $([System.Environment]::OSVersion.VersionString)"
        "Python: $(python --version 2>&1)"
        "Entry point: benchmarks/profile_workload.py"
        "PYTHONPATH: $env:PYTHONPATH"
        "Iterations: $Iterations"
        "Data: data/sample_weather.json"
    ) | Set-Content -Encoding UTF8 (Join-Path $ResultDirectory "environment.txt")

    python .\benchmarks\profile_workload.py --mode baseline --iterations $Iterations --measure-memory --output $BaselineJson
    $BaselineExitCode = $LASTEXITCODE
    python .\benchmarks\profile_workload.py --mode optimized --iterations $Iterations --measure-memory --output $OptimizedJson
    $OptimizedExitCode = $LASTEXITCODE

    python .\scripts\compare_profile_results.py $BaselineJson $OptimizedJson $ComparisonJson 2>&1 |
        Tee-Object -FilePath (Join-Path $ResultDirectory "comparison.log")
    $ComparisonExitCode = $LASTEXITCODE

    python -m cProfile -o $BaselineProfile .\benchmarks\profile_workload.py --mode baseline --iterations $Iterations
    $BaselineProfileExitCode = $LASTEXITCODE
    python -m cProfile -o $OptimizedProfile .\benchmarks\profile_workload.py --mode optimized --iterations $Iterations
    $OptimizedProfileExitCode = $LASTEXITCODE

    python .\scripts\summarize_profile.py $BaselineProfile (Join-Path $ResultDirectory "cpu-baseline.txt")
    python .\scripts\summarize_profile.py $OptimizedProfile (Join-Path $ResultDirectory "cpu-optimized.txt")

    $Comparison = Get-Content -Raw -LiteralPath $ComparisonJson | ConvertFrom-Json
    @(
        "Experiment 3 profiling summary"
        "Result directory: $ResultDirectory"
        "Functional equivalence: $($Comparison.equivalent_results)"
        "Baseline elapsed seconds: $($Comparison.baseline.elapsed_seconds)"
        "Optimized elapsed seconds: $($Comparison.optimized.elapsed_seconds)"
        "Speedup: $($Comparison.speedup)x"
        "Time reduction: $($Comparison.time_reduction_percent)%"
        "Baseline peak bytes: $($Comparison.baseline.peak_bytes)"
        "Optimized peak bytes: $($Comparison.optimized.peak_bytes)"
        "Peak memory reduction: $($Comparison.peak_memory_reduction_percent)%"
        "Exit codes: baseline=$BaselineExitCode, optimized=$OptimizedExitCode, compare=$ComparisonExitCode, baseline_profile=$BaselineProfileExitCode, optimized_profile=$OptimizedProfileExitCode"
    ) | Set-Content -Encoding UTF8 (Join-Path $ResultDirectory "summary.txt")

    Set-Content -Encoding UTF8 (Join-Path $ProjectRoot "reports\experiment-3\LATEST.txt") $ResultDirectory

    if ($BaselineExitCode -ne 0 -or $OptimizedExitCode -ne 0 -or $ComparisonExitCode -ne 0 -or $BaselineProfileExitCode -ne 0 -or $OptimizedProfileExitCode -ne 0) {
        throw "Experiment 3 profiling failed. Inspect $ResultDirectory"
    }
    Write-Host "Experiment 3 profiling passed. Evidence: $ResultDirectory"
}
finally {
    Pop-Location
}
