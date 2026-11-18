# Render every slide of the competition deck to PNG with PowerPoint (Windows), for visual QA.
#   powershell -File scripts/render_deck.ps1 [-Out <folder>]
param([string]$Out = "competition/deck_preview")
$Root = Split-Path -Parent $PSScriptRoot
$Deck = Join-Path $Root "competition\IntegrationRescue_Competition_Deck.pptx"
$Dest = if ([IO.Path]::IsPathRooted($Out)) { $Out } else { Join-Path $Root $Out }
New-Item -ItemType Directory -Force $Dest | Out-Null
$app = New-Object -ComObject PowerPoint.Application
$p = $app.Presentations.Open($Deck, $true, $false, $false)
for ($i = 1; $i -le $p.Slides.Count; $i++) { $p.Slides.Item($i).Export((Join-Path $Dest ("slide{0:D2}.png" -f $i)), "PNG", 1600, 900) }
$p.Close(); $app.Quit()
Write-Host "rendered $($i - 1) slides to $Dest"
