<#
.SYNOPSIS
  IntegrationRescue developer commands (Windows PowerShell).
.EXAMPLE
  ./scripts/dev.ps1 install   # venv + backend + frontend deps
  ./scripts/dev.ps1 backend   # API + simulators on http://127.0.0.1:8000
  ./scripts/dev.ps1 frontend  # dashboard on http://127.0.0.1:5173
  ./scripts/dev.ps1 demo      # run the first incident end-to-end in the terminal
  ./scripts/dev.ps1 test      # backend tests + lint + frontend build + browser tests
  ./scripts/dev.ps1 eval      # deterministic evaluation suite
  ./scripts/dev.ps1 reset     # delete synthetic runtime state under ./var
  ./scripts/dev.ps1 judge-demo  # build dashboard + serve the public-demo mode on http://127.0.0.1:8080
  ./scripts/dev.ps1 verify --url http://127.0.0.1:8080   # end-to-end check (needs $env:IR_ACCESS_TOKEN)
  ./scripts/dev.ps1 record      # fresh live-Gemini judge demo for recording the 2-minute video
  ./scripts/dev.ps1 preflight   # every check to run before deploying (tests, build, container)
#>
param([Parameter(Position = 0)][string]$Command = "help",
      [Parameter(ValueFromRemainingArguments = $true)][string[]]$Rest)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Py = Join-Path $Root ".venv\Scripts\python.exe"

switch ($Command) {
  "install" {
    if (-not (Test-Path $Py)) { python -m venv (Join-Path $Root ".venv") }
    & $Py -m pip install -q --upgrade pip
    & $Py -m pip install -q -e "$Root\backend[dev]"
    npm ci --prefix "$Root\frontend"
    Push-Location "$Root\frontend"; npx playwright install chromium; Pop-Location
  }
  "backend" { & $Py -m uvicorn integrationrescue.api:app --app-dir "$Root\backend" --host 127.0.0.1 --port 8000 }
  "frontend" { npm run dev --prefix "$Root\frontend" }
  "demo" { Push-Location "$Root\backend"; & $Py -m integrationrescue.demo; Pop-Location }
  "test" {
    Push-Location "$Root\backend"
    & "$Root\.venv\Scripts\ruff.exe" check .
    & $Py -m pytest
    Pop-Location
    npm run lint --prefix "$Root\frontend"
    npm run build --prefix "$Root\frontend"
    Push-Location "$Root\frontend"; npx playwright test; Pop-Location
  }
  "eval" { Push-Location "$Root\backend"; & $Py -m integrationrescue.evaluation; Pop-Location }
  "judge-demo" {
    npm run build --prefix "$Root\frontend"
    & $Py "$Root\scripts\serve_demo.py"
  }
  "verify" { & $Py "$Root\scripts\verify_deployment.py" @Rest }
  "record" { & "$Root\scripts\record_demo.ps1" }
  "preflight" { & "$Root\scripts\deploy_preflight.ps1" }
  "reset" {
    $var = Join-Path $Root "var"
    if (Test-Path $var) { Remove-Item -Recurse -Force $var; Write-Host "Removed $var (synthetic data only)" }
  }
  default { Get-Help $PSCommandPath -Detailed }
}
