$venvActivationScript = "venv\scripts\activate.ps1"

if (Test-Path $venvActivationScript) {
    & $venvActivationScript
} else {
    Write-Host "Cannot find '$venvActivationScript'!`n" -f Red
    Exit 1
}

Write-Host "Starting bot..."
python.exe "src/bot.py"