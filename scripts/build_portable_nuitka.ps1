param(
    [string]$Python = ".\venv\Scripts\python.exe",
    [string]$OutputRoot = ".\dist",
    [string]$DistributionName = "CrewAI-Studio-Portable",
    [switch]$InstallBuildDeps,
    [switch]$Clean,
    [switch]$ShowConsole
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $ScriptDir "..")).Path
Set-Location -LiteralPath $RepoRoot

$ResolvedPython = Resolve-Path -LiteralPath $Python -ErrorAction SilentlyContinue
if (-not $ResolvedPython) {
    throw "Python executable not found: $Python. Run install_venv.bat first or pass -Python <path>."
}
$PythonPath = $ResolvedPython.Path

if ($InstallBuildDeps) {
    & $PythonPath -m pip install --upgrade nuitka ordered-set zstandard
}

$NuitkaCacheDir = Join-Path $RepoRoot ".nuitka-cache"
New-Item -ItemType Directory -Force -Path $NuitkaCacheDir | Out-Null
$env:NUITKA_CACHE_DIR = $NuitkaCacheDir

$PythonInfo = & $PythonPath -c "import json, sys, sysconfig; print(json.dumps({'base_executable': getattr(sys, '_base_executable', sys.executable), 'base_prefix': sys.base_prefix, 'prefix': sys.prefix, 'purelib': sysconfig.get_paths()['purelib']}))" | ConvertFrom-Json
$BaseLib = Join-Path $PythonInfo.base_prefix "Lib"
$BaseDlls = Join-Path $PythonInfo.base_prefix "DLLs"
$BaseRuntimeRoot = Split-Path -Parent $PythonInfo.base_executable
$SitePackages = $PythonInfo.purelib

& $PythonPath -m nuitka --version | Out-Host
if ($LASTEXITCODE -ne 0) {
    throw "Nuitka command failed. Check the output above, or re-run with -InstallBuildDeps if Nuitka is missing."
}

$ResolvedOutputRoot = Join-Path $RepoRoot $OutputRoot
$LauncherBuildRoot = Join-Path $ResolvedOutputRoot "nuitka-build"
$StopBuildRoot = Join-Path $ResolvedOutputRoot "nuitka-stop-build"
$PackageDir = Join-Path $ResolvedOutputRoot $DistributionName

if ($Clean) {
    foreach ($Path in @($LauncherBuildRoot, $StopBuildRoot, $PackageDir)) {
        $Resolved = Resolve-Path -LiteralPath $Path -ErrorAction SilentlyContinue
        if ($Resolved -and $Resolved.Path.StartsWith($RepoRoot)) {
            Remove-Item -LiteralPath $Resolved.Path -Recurse -Force
        }
    }
}

New-Item -ItemType Directory -Force -Path $LauncherBuildRoot | Out-Null
New-Item -ItemType Directory -Force -Path $StopBuildRoot | Out-Null

$env:PYTHONPATH = "$RepoRoot\app;$RepoRoot;$env:PYTHONPATH"

function Invoke-RobocopyChecked {
    param(
        [string]$Source,
        [string]$Destination,
        [string[]]$ExtraArgs = @()
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        throw "Copy source not found: $Source"
    }

    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    $args = @($Source, $Destination, "/E", "/NFL", "/NDL", "/NJH", "/NJS", "/NP") + $ExtraArgs
    & robocopy @args | Out-Host
    if ($LASTEXITCODE -gt 7) {
        throw "Robocopy failed from $Source to $Destination with exit code $LASTEXITCODE"
    }
    $global:LASTEXITCODE = 0
}

$ConsoleMode = if ($ShowConsole) { "force" } else { "disable" }
$NuitkaArgs = @(
    "portable_launcher.py",
    "--mode=standalone",
    "--mingw64",
    "--assume-yes-for-downloads",
    "--lto=no",
    "--output-dir=$LauncherBuildRoot",
    "--output-filename=CrewAI Studio.exe",
    "--windows-console-mode=$ConsoleMode",
    "--windows-icon-from-ico=img/favicon.ico",
    "--include-package=urllib",
    "--report=$LauncherBuildRoot\nuitka-report.xml"
)

& $PythonPath -m nuitka @NuitkaArgs
if ($LASTEXITCODE -ne 0) {
    throw "Nuitka launcher build failed."
}

$StopNuitkaArgs = @(
    "portable_stop.py",
    "--mode=standalone",
    "--mingw64",
    "--assume-yes-for-downloads",
    "--lto=no",
    "--output-dir=$StopBuildRoot",
    "--output-filename=Stop CrewAI Studio.exe",
    "--windows-console-mode=force",
    "--windows-icon-from-ico=img/favicon.ico",
    "--report=$StopBuildRoot\nuitka-report.xml"
)

& $PythonPath -m nuitka @StopNuitkaArgs
if ($LASTEXITCODE -ne 0) {
    throw "Nuitka stop build failed."
}

$NuitkaDist = Join-Path $LauncherBuildRoot "portable_launcher.dist"
if (-not (Test-Path -LiteralPath $NuitkaDist)) {
    throw "Expected Nuitka output not found: $NuitkaDist"
}

$StopNuitkaDist = Join-Path $StopBuildRoot "portable_stop.dist"
if (-not (Test-Path -LiteralPath $StopNuitkaDist)) {
    throw "Expected Nuitka stop output not found: $StopNuitkaDist"
}

if (Test-Path -LiteralPath $PackageDir) {
    Remove-Item -LiteralPath $PackageDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $PackageDir | Out-Null

Copy-Item -Path (Join-Path $NuitkaDist "*") -Destination $PackageDir -Recurse -Force
Copy-Item -Path (Join-Path $StopNuitkaDist "*") -Destination $PackageDir -Recurse -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot "app") -Destination (Join-Path $PackageDir "app") -Recurse -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot "img") -Destination (Join-Path $PackageDir "img") -Recurse -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot ".streamlit") -Destination (Join-Path $PackageDir ".streamlit") -Recurse -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot ".env_example") -Destination (Join-Path $PackageDir ".env_example") -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot ".env_example") -Destination (Join-Path $PackageDir ".env") -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot "requirements.txt") -Destination (Join-Path $PackageDir "requirements.txt") -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot "LICENCE") -Destination (Join-Path $PackageDir "LICENCE") -Force

$RuntimeDir = Join-Path $PackageDir "python-runtime"
$RuntimeLib = Join-Path $RuntimeDir "Lib"
$RuntimeDlls = Join-Path $RuntimeDir "DLLs"
$RuntimeSitePackages = Join-Path $RuntimeLib "site-packages"

New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null
foreach ($Pattern in @("python.exe", "pythonw.exe", "python*.dll", "vcruntime*.dll")) {
    Get-ChildItem -LiteralPath $BaseRuntimeRoot -Filter $Pattern -File -ErrorAction SilentlyContinue | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $RuntimeDir $_.Name) -Force
    }
}

if (-not (Test-Path -LiteralPath (Join-Path $RuntimeDir "python.exe"))) {
    Copy-Item -LiteralPath $PythonInfo.base_executable -Destination (Join-Path $RuntimeDir "python.exe") -Force
}

Invoke-RobocopyChecked -Source $BaseLib -Destination $RuntimeLib -ExtraArgs @(
    "/XD",
    "site-packages",
    "__pycache__",
    "test",
    "tests",
    "idlelib",
    "tkinter",
    "turtledemo",
    "ensurepip",
    "/XF",
    "*.pyc",
    "*.pyo"
)

if (Test-Path -LiteralPath $BaseDlls) {
    Invoke-RobocopyChecked -Source $BaseDlls -Destination $RuntimeDlls -ExtraArgs @("/XF", "*.pdb")
}

Invoke-RobocopyChecked -Source $SitePackages -Destination $RuntimeSitePackages -ExtraArgs @(
    "/XD",
    "__pycache__",
    "test",
    "tests",
    "testing",
    ".pytest_cache",
    "/XF",
    "*.pyc",
    "*.pyo"
)

New-Item -ItemType Directory -Force -Path (Join-Path $PackageDir "knowledge") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $PackageDir "logs") | Out-Null

Write-Host ""
Write-Host "Portable package created:"
Write-Host "  $PackageDir"
Write-Host ""
Write-Host "Run:"
Write-Host "  `"$PackageDir\CrewAI Studio.exe`""
