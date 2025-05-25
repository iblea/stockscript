# 현재 스크립트가 있는 디렉토리로 이동
Set-Location $PSScriptRoot

# start.ps1 경로 설정
$startScriptPath = Join-Path $PSScriptRoot "start.ps1"

# start.ps1이 존재하는지 확인
if (-not (Test-Path $startScriptPath)) {
    Write-Host "start.ps1 file not found at: $startScriptPath" -ForegroundColor Red
    exit 1
}

try {
    # PowerShell을 백그라운드에서 실행 (새 창 없이)
    $process = Start-Process -FilePath "powershell.exe" `
                           -ArgumentList "-ExecutionPolicy Bypass -File `"$startScriptPath`"" `
                           -WindowStyle Hidden `
                           -PassThru

    Write-Host "start.ps1 started in background (PID: $($process.Id))" -ForegroundColor Green
    Write-Host "Process details:" -ForegroundColor Cyan
    Write-Host "  - Process ID: $($process.Id)" -ForegroundColor White
    Write-Host "  - Process Name: $($process.ProcessName)" -ForegroundColor White
    Write-Host "  - Start Time: $($process.StartTime)" -ForegroundColor White
}
catch {
    Write-Host "Error starting background process: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`nBackground process started successfully!" -ForegroundColor Green
# $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")