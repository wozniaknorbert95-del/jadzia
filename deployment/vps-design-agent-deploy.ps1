# Design Agent v3.1 — jadzia + VGE non-interactive deploy (from Windows Git Bash / WSL)
# Usage: bash deployment/vps-design-agent-deploy.ps1
# Prereq: ~/.ssh/cyberfolks_key, local jadzia-core on feat/design-agent-v31

$ErrorActionPreference = "Stop"
$VPS = "root@185.243.54.115"
$KEY = "$env:USERPROFILE\.ssh\cyberfolks_key"
$JADZIA_LOCAL = "c:\Users\FlexGrafik\FlexGrafik\github\jadzia-core"
$VGE_LOCAL = "c:\Users\FlexGrafik\FlexGrafik\github\image generator"

function Invoke-Ssh($cmd) {
    ssh -i $KEY -p 22 -o StrictHostKeyChecking=no $VPS $cmd
}

Write-Host "=== 1. Upload jadzia-core ==="
scp -i $KEY -r -o StrictHostKeyChecking=no `
    "$JADZIA_LOCAL\api" `
    "$JADZIA_LOCAL\agent" `
    "$JADZIA_LOCAL\core" `
    "${VPS}:/opt/jadzia/"

Write-Host "=== 2. Upload VGE (image generator) ==="
Invoke-Ssh "mkdir -p /opt/vge/image-generator"
scp -i $KEY -r -o StrictHostKeyChecking=no `
    "$VGE_LOCAL\vge" `
    "$VGE_LOCAL\tests" `
    "$VGE_LOCAL\data" `
    "$VGE_LOCAL\requirements.txt" `
    "${VPS}:/opt/vge/image-generator/"

Write-Host "=== 3. Upload SSoT mirror ==="
$SSOT = "c:\Users\FlexGrafik\FlexGrafik\github\zzpackage.flexgrafik.nl\system\data\product-master-table.json"
Invoke-Ssh "mkdir -p /opt/zzpackage/system/data"
scp -i $KEY -o StrictHostKeyChecking=no $SSOT "${VPS}:/opt/zzpackage/system/data/product-master-table.json"

Write-Host "=== 4. Run VPS setup + restart ==="
scp -i $KEY -o StrictHostKeyChecking=no "$JADZIA_LOCAL\deployment\vps-design-agent-setup.sh" "${VPS}:/opt/jadzia/deployment/"
Invoke-Ssh "chmod +x /opt/jadzia/deployment/vps-design-agent-setup.sh && bash /opt/jadzia/deployment/vps-design-agent-setup.sh"

Write-Host "=== 5. Probe route ==="
Invoke-Ssh "curl -s -o /dev/null -w 'design-agent: %{http_code}\n' -X POST http://127.0.0.1:8000/api/v1/design-agent/generate"
