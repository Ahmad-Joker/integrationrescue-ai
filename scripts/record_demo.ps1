# One-command setup for recording the live Gemini demo (Windows PowerShell).
#   ./scripts/record_demo.ps1            # or: ./scripts/dev.ps1 record
#
# Builds the dashboard, starts a fresh judge-demo server on http://127.0.0.1:8080 with live Gemini as the default
# decision maker (the model used for all recorded live results), and opens the browser. Needs GEMINI_API_KEY in .env.
# Fresh fictional state each time (var\recording). Throwaway access/admin codes are generated for this session only
# and printed in this console; never show this console on camera. Stop with Ctrl+C.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Py = Join-Path $Root ".venv\Scripts\python.exe"
$envFile = Join-Path $Root ".env"
if (-not ((Test-Path $envFile) -and (Select-String -Path $envFile -Pattern '^\s*GEMINI_API_KEY\s*=\s*\S' -Quiet))) {
  if (-not $env:GEMINI_API_KEY) { throw "GEMINI_API_KEY is not set (.env or environment): the demo must use live Gemini" }
}
npm run build --prefix "$Root\frontend" | Out-Null
$state = Join-Path $Root "var\recording"
if (Test-Path $state) { Remove-Item -Recurse -Force $state }
$env:IR_VAR_DIR = $state
$env:IR_PROVIDER = "gemini"
if (-not $env:IR_GEMINI_MODEL) { $env:IR_GEMINI_MODEL = "gemini-3.1-flash-lite" }
$env:IR_ACCESS_TOKEN = & $Py -c "import secrets; print(secrets.token_urlsafe(18))"
$env:IR_ADMIN_TOKEN = & $Py -c "import secrets; print(secrets.token_urlsafe(18))"
Write-Host "Access code for this recording session (type it into the banner, keep this window off camera):"
Write-Host "  $env:IR_ACCESS_TOKEN"
Write-Host "Model: $env:IR_GEMINI_MODEL  ·  state: $state  ·  checklist: competition\LIVE_DEMO_CHECKLIST.md"
Start-Job { Start-Sleep 4; Start-Process "http://127.0.0.1:8080/#/new" } | Out-Null
& $Py (Join-Path $Root "scripts\serve_demo.py")
