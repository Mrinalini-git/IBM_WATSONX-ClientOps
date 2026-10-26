# ==============================================================================
# ClientOps AI - IBM Cloud Code Engine Deployment Script
# Deploys ClientOps AI as a serverless container website on IBM Cloud
# ==============================================================================

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  ClientOps AI - Deploy to IBM Cloud Code Engine" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check IBM Cloud CLI
if (-not (Get-Command ibmcloud -ErrorAction SilentlyContinue)) {
    Write-Host "[!] IBM Cloud CLI not detected." -ForegroundColor Yellow
    Write-Host "    Install from: https://cloud.ibm.com/docs/cli" -ForegroundColor Yellow
    Write-Host "    Or run: powershell -Command 'iex (New-Object Net.WebClient).DownloadString(\"https://clis.cloud.ibm.com/install/powershell\")'"
    exit 1
}

# 2. Check login
Write-Host "`n[1/4] Checking IBM Cloud session..." -ForegroundColor Green
ibmcloud target

# 3. Create or select Code Engine project
$PROJECT_NAME = "clientops-ai-project"
Write-Host "`n[2/4] Initializing Code Engine Project: $PROJECT_NAME..." -ForegroundColor Green
ibmcloud ce project create --name $PROJECT_NAME 2>$null
ibmcloud ce project select --name $PROJECT_NAME

# 4. Deploy Application from source directory
$APP_NAME = "clientops-ai-web"
Write-Host "`n[3/4] Building and deploying application: $APP_NAME..." -ForegroundColor Green
ibmcloud ce app create --name $APP_NAME `
    --build-source . `
    --port 8000 `
    --min-scale 1 `
    --max-scale 3 `
    --cpu 0.5 `
    --memory 1G `
    --env ENVIRONMENT=production `
    --env GRANITE_MODEL_ID=ibm/granite-3-8b-instruct

# 5. Retrieve Public URL
Write-Host "`n[4/4] Application Deployed Successfully!" -ForegroundColor Green
$APP_URL = ibmcloud ce app get --name $APP_NAME --output json | ConvertFrom-Json | Select-Object -ExpandProperty status | Select-Object -ExpandProperty url
Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "  Public Website URL: $APP_URL" -ForegroundColor Yellow
Write-Host "  Swagger API Docs:   $APP_URL/docs" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
