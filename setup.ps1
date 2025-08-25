if ((Get-Item .).FullName -ne $PSScriptRoot) {
    Write-Host "Please run the script from its directory." -f Red
    Exit
}

if (!(Get-Command python.exe -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed or is not set in PATH." -f Red
    Exit
}

$userPyVer = &{python.exe --version}
$userPyVer = $userPyVer.Split(" ")[1]
$reqPyVer = "3.11.0"

if ([System.Version]$userPyVer -lt [System.Version]$reqPyVer) {
    Write-Host "Your Python version ($userPyVer) is not supported." `
               "Please install Python $reqPyVer or greater to continue." -f Red
    Exit
}

$venvActivationScript = "venv\scripts\activate.ps1"

if (Test-Path $venvActivationScript) {
    if (($null -eq $env:VIRTUAL_ENV) -or !(Test-Path $env:VIRTUAL_ENV)) {
        Write-Host "Activating virtual environment..."
        & $venvActivationScript   
    }
} else {
    Write-Host "Creating virtual environment..."
    python.exe -m venv venv
    Write-Host "Activating virtual environment..."
    & $venvActivationScript
}

# Make sure venv is actually activated
if ($null -eq $env:VIRTUAL_ENV) {
    Write-Host "Python virtual environment (venv) could not be activated." `
               "Please try activating it manually by executing" `
               "'$venvActivationScript'." -f Red
    Exit
}

$env:PIP_DISABLE_PIP_VERSION_CHECK=1

function Get-MissingPipPackages {
    param([string]$RequirementsFile)

    $installedPackages = pip.exe list --format=freeze
    $requiredPackages = Get-Content $RequirementsFile
    $missingPackages = @()

    foreach ($package in $requiredPackages) {
        $installed = $installedPackages | Where-Object { $_ -match "^$package" }
        if (!$installed) {
            $missingPackages += $package
        }
    }

    return $missingPackages
}

[array]$missingPackages = Get-MissingPipPackages "requirements.txt"
if ($missingPackages.Count -gt 0) {
    $missingPackages | ForEach-Object {
        pip.exe install $_
    }
}

$loggingEnabled = (
    Get-Content -Path "config.json" -Raw | ConvertFrom-Json
).logging.enabled -eq $true

if ($loggingEnabled) {
    New-Item -ItemType Directory "logs" -Force | Out-Null
}