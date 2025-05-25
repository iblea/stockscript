# # 관리자 권한 확인 및 자동 승격
# if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
#     Write-Host "Requesting administrator privileges..." -ForegroundColor Yellow
#
#     # 현재 스크립트를 관리자 권한으로 재실행
#     Start-Process powershell.exe -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
#
#     # 현재 프로세스 종료
#     exit
# }
#
# Write-Host "Running with administrator privileges..." -ForegroundColor Green

# main.py 프로세스가 실행 중인지 확인하고 종료
try {
    $mainPyProcess = Get-WmiObject Win32_Process | Where-Object {
        $_.Name -eq "python.exe" -and
        $_.CommandLine -like "*kiwoom*src*main.py*"
    }

    if ($mainPyProcess) {
        Write-Host "Found main.py process:" -ForegroundColor Yellow
        Write-Host "  - PID: $($mainPyProcess.ProcessId)" -ForegroundColor White
        Write-Host "  - Name: $($mainPyProcess.Name)" -ForegroundColor White
        Write-Host "  - CommandLine: $($mainPyProcess.CommandLine)" -ForegroundColor White

        Write-Host "`nTerminating process..." -ForegroundColor Red

        try {
            # PowerShell 네이티브 Stop-Process 사용
            $targetPid = $mainPyProcess.ProcessId
            Stop-Process -Id $targetPid -Force

            Write-Host "Process terminated successfully!" -ForegroundColor Green
        }
        catch {
            Write-Host "Error terminating process: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    else {
        Write-Host "No main.py process found running." -ForegroundColor Green
    }
}
catch {
    Write-Host "Error checking for processes: $($_.Exception.Message)" -ForegroundColor Red
}


# logs 디렉토리의 모든 파일 제거
Write-Host "`nWaiting 2 seconds before cleaning logs..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

try {
    $logsPath = Join-Path $PSScriptRoot "logs"

    if (Test-Path $logsPath -PathType Container) {
        Write-Host "`nCleaning logs directory..." -ForegroundColor Yellow

        $logFiles = Get-ChildItem -Path $logsPath -File
        if ($logFiles.Count -gt 0) {
            Remove-Item -Path "$logsPath\*" -Force -Recurse
            Write-Host "Removed $($logFiles.Count) files from logs directory." -ForegroundColor Green
        } else {
            Write-Host "logs directory is already empty." -ForegroundColor Green
        }
    }
    else {
        Write-Host "`nlogs directory not found." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Error cleaning logs directory: $($_.Exception.Message)" -ForegroundColor Red
}



Write-Host "`nDone." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
