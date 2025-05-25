Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' 완전 숨김 모드로 PowerShell 실행
objShell.Run "powershell.exe -WindowStyle Hidden -NoProfile -NonInteractive -NoLogo -ExecutionPolicy Bypass -File C:\background.ps1", 0, False

' 스크립트 즉시 종료
WScript.Quit
