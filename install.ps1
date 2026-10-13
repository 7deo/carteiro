$ErrorActionPreference = "Stop"

$repository = "7deo/carteiro"
$branch = if ($env:CARTEIRO_BRANCH) { $env:CARTEIRO_BRANCH } else { "main" }
$installRoot = if ($env:CARTEIRO_HOME) {
    $env:CARTEIRO_HOME
} else {
    Join-Path $env:LOCALAPPDATA "Carteiro"
}
$binDirectory = Join-Path $installRoot "bin"
$archiveUrl = "https://github.com/$repository/archive/refs/heads/$branch.zip"
$temporaryDirectory = Join-Path ([System.IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())

$pythonCommand = Get-Command py, python -ErrorAction SilentlyContinue |
    Select-Object -First 1
if (-not $pythonCommand) {
    throw "Python 3.10 ou superior nao encontrado. Instale o Python e tente novamente."
}

$pythonArguments = @()
if ($pythonCommand.Name -eq "py") {
    $pythonArguments = @("-3")
}
$pythonVersion = & $pythonCommand.Source @pythonArguments -c "import sys; print('%d.%d' % sys.version_info[:2])"
if ($LASTEXITCODE -ne 0 -or [version]$pythonVersion -lt [version]"3.10") {
    throw "O Carteiro requer Python 3.10 ou superior."
}

try {
    New-Item -ItemType Directory -Path $temporaryDirectory | Out-Null
    $archivePath = Join-Path $temporaryDirectory "carteiro.zip"
    $extractPath = Join-Path $temporaryDirectory "source"
    Write-Host "Baixando O Carteiro de $repository..."
    Invoke-WebRequest -Uri $archiveUrl -OutFile $archivePath
    Expand-Archive -Path $archivePath -DestinationPath $extractPath
    $project = Get-ChildItem -Path $extractPath -Directory |
        Where-Object { Test-Path (Join-Path $_.FullName "pyproject.toml") } |
        Select-Object -First 1
    if (-not $project) {
        throw "O arquivo baixado nao contem o projeto esperado."
    }

    New-Item -ItemType Directory -Path $installRoot -Force | Out-Null
    New-Item -ItemType Directory -Path $binDirectory -Force | Out-Null
    $venvPython = Join-Path $installRoot "venv\Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        & $pythonCommand.Source @pythonArguments -m venv (Join-Path $installRoot "venv")
        if ($LASTEXITCODE -ne 0) {
            throw "Nao foi possivel criar o ambiente Python do Carteiro."
        }
    }
    & $venvPython -m pip install --disable-pip-version-check $project.FullName
    if ($LASTEXITCODE -ne 0) {
        throw "Nao foi possivel instalar o Carteiro."
    }

    $launcherPath = Join-Path $binDirectory "carteiro.cmd"
$launcher = @"
@echo off
"$venvPython" -m carteiro %*
"@
    Set-Content -Path $launcherPath -Value $launcher -Encoding Ascii

    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $pathEntries = @($userPath -split ";" | Where-Object { $_ })
    if (-not ($pathEntries | Where-Object { $_.TrimEnd("\") -ieq $binDirectory.TrimEnd("\") })) {
        $updatedPath = (@($pathEntries) + $binDirectory) -join ";"
        [Environment]::SetEnvironmentVariable("Path", $updatedPath, "User")
    }
    $env:Path = "$binDirectory;$env:Path"

    Write-Host "Instalacao concluida. Abra um novo terminal e execute:"
    Write-Host 'carteiro "noticias do Brasil"'
}
finally {
    if (Test-Path $temporaryDirectory) {
        Remove-Item -Path $temporaryDirectory -Recurse -Force
    }
}
