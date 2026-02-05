$logFile = "logs\agent.log"
$startTime = Get-Date

Write-Host "=== JADZIA FIELD TEST MONITOR ===" -ForegroundColor Cyan
Write-Host "Started: $startTime" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow

$metrics = @{
    total_tasks = 0
    quality_checks = 0
    quality_failures = 0
    quality_retries = 0
    verifications = 0
    verification_failures = 0
    auto_rollbacks = 0
    security_blocks = 0
}

# Upewnij się, że plik logu istnieje, jeśli nie - czekaj
while (-not (Test-Path $logFile)) {
    Write-Host "Waiting for logs/agent.log to be created..." -ForegroundColor Gray
    Start-Sleep -Seconds 2
}

Get-Content $logFile -Wait -Tail 0 | ForEach-Object {
    $line = $_
    
    # Count tasks
    if ($line -match "operation_id") { $metrics.total_tasks++ }
    
    # Quality checks
    if ($line -match "\[QUALITY\] Starting validation") { $metrics.quality_checks++ }
    if ($line -match "\[QUALITY\] Validation FAILED") { $metrics.quality_failures++ }
    if ($line -match "\[GENERATE\].*regenerating") { $metrics.quality_retries++ }
    
    # Verifications
    if ($line -match "\[VERIFICATION\] Starting") { $metrics.verifications++ }
    if ($line -match "\[VERIFICATION\] FAILED") { $metrics.verification_failures++ }
    if ($line -match "AUTO-ROLLBACK") { $metrics.auto_rollbacks++ }
    
    # Security
    if ($line -match "\[SECURITY\].*blocked") { $metrics.security_blocks++ }
    
    # Print the line clearly
    if ($line -match "\[QUALITY\]|\[VERIFICATION\]|\[SECURITY\]|\[ROLLBACK\]") {
        $color = switch -Regex ($line) {
            "FAILED|ERROR" { "Red" }
            "PASSED|SUCCESS" { "Green" }
            "WARNING" { "Yellow" }
            default { "White" }
        }
        Write-Host $line -ForegroundColor $color
    }
    
    # Update dashboard every 10 tasks or roughly periodically if needed (logic simplified here)
    if ($metrics.total_tasks % 10 -eq 0 -and $metrics.total_tasks -gt 0) {
        # Dashboard logic remains same as spec
    }
}
