$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Target = Join-Path $ProjectRoot ".local-packages"

python -m pip install --disable-pip-version-check --upgrade --target $Target -r (Join-Path $ProjectRoot "requirements-dev.txt")
if ($LASTEXITCODE -ne 0) {
    throw "依赖安装失败，pip 退出码为 $LASTEXITCODE"
}

Write-Host "依赖已安装到 $Target"
