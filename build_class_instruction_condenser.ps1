param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$AppName = "ClassInstructionCondenser"

if (-not (Test-Path $VenvPython)) {
    python -m venv (Join-Path $ProjectRoot ".venv")
}

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r (Join-Path $ProjectRoot "requirements-class-condenser.txt")

if ($Clean) {
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue `
        (Join-Path $ProjectRoot "build"), `
        (Join-Path $ProjectRoot "dist\$AppName"), `
        (Join-Path $ProjectRoot "$AppName.spec")
}

& $VenvPython -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name $AppName `
    --paths $ProjectRoot `
    --distpath (Join-Path $ProjectRoot "dist") `
    --workpath (Join-Path $ProjectRoot "build") `
    --specpath $ProjectRoot `
    (Join-Path $ProjectRoot "class_instruction_summarizer\__main__.py")

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

Write-Host ""
Write-Host "Executable created:"
Write-Host (Join-Path $ProjectRoot "dist\$AppName\$AppName.exe")
