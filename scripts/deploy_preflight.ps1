# Everything to check before deploying the judge demo (Windows PowerShell, Docker Desktop running).
#   ./scripts/deploy_preflight.ps1        # or: ./scripts/dev.ps1 preflight
#
# Runs the CI-equivalent checks, builds the container, proves it refuses to start without an access code, then runs
# the 15 end-to-end judge-flow checks against it with the deterministic baseline (no model key, no cost). Throwaway
# codes live only in this process. Exit code 0 only if everything passed.
# Continue, not Stop: Windows PowerShell 5.1 turns any native stderr (such as the expected refusal below) into a
# terminating error. Every step is judged by its exit code instead.
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
$Py = Join-Path $Root ".venv\Scripts\python.exe"
$failed = @()
function Step($name, [scriptblock]$body) {
  Write-Host "`n== $name" -ForegroundColor Cyan
  & $body
  if ($LASTEXITCODE -ne 0) { $script:failed += $name; Write-Host "FAILED: $name" -ForegroundColor Red }
  else { Write-Host "ok: $name" -ForegroundColor Green }
}

Step "render.yaml uses the tested model and the free plan" {
  $y = Get-Content (Join-Path $Root "render.yaml") -Raw
  if ($y -match "gemini-3\.1-flash-lite" -and $y -match "plan:\s*free" -and $y -match "IR_ACCESS_TOKEN\s*\r?\n\s*sync:\s*false") {
    $global:LASTEXITCODE = 0 } else { $global:LASTEXITCODE = 1 }
}
Step "backend lint" { Push-Location "$Root\backend"; & "$Root\.venv\Scripts\ruff.exe" check .; Pop-Location }
Step "backend tests" { Push-Location "$Root\backend"; & $Py -m pytest -q -rf --tb=short; Pop-Location }
Step "frontend lint" { npm run lint --prefix "$Root\frontend" }
Step "frontend build" { npm run build --prefix "$Root\frontend" }
Step "docker build" { docker build -q -t integrationrescue:preflight $Root }
Step "container refuses to start without an access code" {
  cmd /c 'docker run --rm integrationrescue:preflight python -c "import integrationrescue.api" >nul 2>&1'
  $global:LASTEXITCODE = if ($LASTEXITCODE -ne 0) { 0 } else { 1 }
}
$env:IR_ACCESS_TOKEN = & $Py -c "import secrets; print(secrets.token_urlsafe(18))"
$admin = & $Py -c "import secrets; print(secrets.token_urlsafe(18))"
docker rm -f ir-preflight 2>$null | Out-Null
docker run -d --name ir-preflight -p 8095:8000 -e IR_ACCESS_TOKEN -e "IR_ADMIN_TOKEN=$admin" integrationrescue:preflight | Out-Null
for ($i = 0; $i -lt 60; $i++) { try { Invoke-RestMethod http://127.0.0.1:8095/api/health | Out-Null; break } catch { Start-Sleep 1 } }
Step "judge flow in the container (15 checks, deterministic)" {
  & $Py "$Root\scripts\verify_deployment.py" --url http://127.0.0.1:8095 --timeout 300
}
docker rm -f ir-preflight | Out-Null
Remove-Item Env:IR_ACCESS_TOKEN

if ($failed.Count) { Write-Host "`nPREFLIGHT FAILED: $($failed -join ', ')" -ForegroundColor Red; exit 1 }
Write-Host "`nPREFLIGHT PASSED: safe to deploy (next: competition/USER_ACTIONS.md A4)" -ForegroundColor Green
