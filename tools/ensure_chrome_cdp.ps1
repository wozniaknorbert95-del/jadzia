# Keep Chrome CDP alive on :9222 using the user's Default profile (session cookies).
# Cursor Simple Browser (WebView2) is NOT CDP-controllable — this is the agent bridge.
$ErrorActionPreference = "Stop"
$chrome = "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
$userData = "$env:LOCALAPPDATA\Google\Chrome\User Data"
$url = if ($args[0]) { $args[0] } else { "https://www.tiktok.com/tiktokstudio/upload" }

function Test-Cdp {
  try {
    Invoke-WebRequest -Uri "http://127.0.0.1:9222/json/version" -UseBasicParsing -TimeoutSec 2 | Out-Null
    return $true
  } catch { return $false }
}

if (Test-Cdp) {
  Write-Output "CDP_OK already listening on 9222"
  exit 0
}

if (-not (Test-Path $chrome)) { Write-Error "Chrome not found: $chrome"; exit 1 }

Start-Process -FilePath $chrome -ArgumentList @(
  "--remote-debugging-port=9222",
  "--user-data-dir=$userData",
  "--profile-directory=Default",
  "--new-window",
  $url
)

$deadline = (Get-Date).AddSeconds(20)
while ((Get-Date) -lt $deadline) {
  if (Test-Cdp) { Write-Output "CDP_OK started"; exit 0 }
  Start-Sleep -Milliseconds 500
}
Write-Error "CDP_FAIL: port 9222 not up"
exit 1
