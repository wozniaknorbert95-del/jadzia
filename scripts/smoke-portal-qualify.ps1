# INT-012 Phase 1 smoke — POST /api/v1/portal/qualify
# Usage: .\scripts\smoke-portal-qualify.ps1 [-BaseUrl https://api.zzpackage.flexgrafik.nl]

param(
    [string]$BaseUrl = "https://api.zzpackage.flexgrafik.nl"
)

$ErrorActionPreference = "Stop"
$endpoint = "$BaseUrl/api/v1/portal/qualify"
$sid = "smoke-$(Get-Date -Format 'yyyyMMddHHmmss')"

function Invoke-Qualify($body) {
    $json = $body | ConvertTo-Json -Compress
    $r = Invoke-RestMethod -Uri $endpoint -Method POST -ContentType "application/json" -Body $json -TimeoutSec 30
    return $r
}

Write-Host "=== D1-2 Greeting ===" -ForegroundColor Cyan
$r1 = Invoke-Qualify @{ session_id = $sid; message = ""; step = "greeting" }
if ($r1.schema_version -ne "qual_v1" -or $r1.step_next -ne "q1_industry") { throw "D1-2 FAIL: $($r1 | ConvertTo-Json -Compress)" }
Write-Host "PASS step_next=$($r1.step_next)"

Write-Host "=== D1-3 Funnel groeier ===" -ForegroundColor Cyan
$flow = @(
    @{ step = "q1_industry"; message = "bouw" },
    @{ step = "q2_goal"; message = "voertuig reclame" },
    @{ step = "q3_vehicle"; message = "bedrijfsbus" },
    @{ step = "q4_budget"; message = "300-700" }
)
$last = $null
foreach ($turn in $flow) {
    $last = Invoke-Qualify @{ session_id = $sid; message = $turn.message; step = $turn.step }
}
if ($last.recommended_preset_id -ne "groeier" -or $last.cta.type -ne "wizard") { throw "D1-3 FAIL: $($last | ConvertTo-Json -Compress)" }
if ($last.wizard_deep_link -notmatch "preset=groeier" -or $last.wizard_deep_link -notmatch "utm_source=portal_qual") { throw "D1-3 deep link FAIL" }
Write-Host "PASS preset=groeier"

Write-Host "=== D1-4 Funnel flota ===" -ForegroundColor Cyan
$sid2 = "$sid-flota"
Invoke-Qualify @{ session_id = $sid2; message = "Hoi"; step = "greeting" } | Out-Null
$flota = @(
    @{ step = "q1_industry"; message = "techniek" },
    @{ step = "q2_goal"; message = "vloot" },
    @{ step = "q3_vehicle"; message = "vloot" },
    @{ step = "q4_budget"; message = "700+" }
)
$lastF = $null
foreach ($turn in $flota) {
    $lastF = Invoke-Qualify @{ session_id = $sid2; message = $turn.message; step = $turn.step }
}
if ($lastF.recommended_preset_id -ne "professional-flota" -or $lastF.cta.type -ne "whatsapp") { throw "D1-4 FAIL" }
Write-Host "PASS preset=professional-flota whatsapp CTA"

Write-Host "=== ALL SMOKE PASS ===" -ForegroundColor Green
