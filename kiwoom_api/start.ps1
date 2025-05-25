# 현재 스크립트가 있는 디렉토리로 이동
Set-Location $PSScriptRoot

# 가상환경 디렉토리명 변수 설정
$venvName = "kiwoom"
$mainScript = ".\src\main.py"

# 가상환경 디렉토리 경로
$venvPath = Join-Path $PSScriptRoot $venvName
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
$deactivateScript = Join-Path $venvPath "Scripts\deactivate.bat"

if (-not (Test-Path $venvPath -PathType Container)) {
    Write-Host "$venvName directory not found. create venv..." -ForegroundColor Yellow

    try {
        # Python 가상환경 생성
        python -m venv $venvName
        Write-Host "create venv done!" -ForegroundColor Green

        # 가상환경 활성화 방법 안내
        Write-Host "`nactivate venv: $activateScript" -ForegroundColor Cyan
        Write-Host "$activateScript" -ForegroundColor White
    }
    catch {
        Write-Host "create venv error: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# main.py 프로세스가 실행 중인지 확인 (WMI 사용)
try {
    $mainPyProcess = Get-WmiObject Win32_Process | Where-Object {
        $_.Name -eq "python.exe" -and
        $_.CommandLine -like "*kiwoom*src*main.py*"
    }

    if ($mainPyProcess) {
        Write-Host "main.py is already running `n (PID: $($mainPyProcess.ProcessId) `n $($mainPyProcess.Name) `n $($mainPyProcess.CommandLine)). Skipping execution." -ForegroundColor Yellow
        # $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        # exit 1
        exit 0
    }
    else {
        Write-Host "Starting main.py..." -ForegroundColor Green
    }
}
catch {
    Write-Host "Error checking process. Starting main.py..." -ForegroundColor Yellow
}



& $activateScript

python -m pip list

Write-Host "`n"

python $mainScript

& $deactivateScript

# 잠시 대기 (선택사항)
# Write-Host "`nPress any key to exit..."
# $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")


