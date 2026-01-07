# Runs in current projects context

$ScriptFolder = $PSScriptRoot

if (-not $ScriptFolder) {
    $ScriptFolder = Split-Path -Parent $MyInvocation.MyCommand.Path
}

Write-Host "Running from: $ScriptFolder"

Set-Location $ScriptFolder
& "$ScriptFolder\.venv\Scripts\Activate.ps1"
python "$ScriptFolder\main.py"

# Clean up logs older than 30 days
$LogFolder = "$ScriptFolder\logs"
$CutoffDate = (Get-Date).AddDays(-30)
$DeletedLogs = Get-ChildItem "$LogFolder\*.log" -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -lt $CutoffDate }

if ($DeletedLogs) {
    $DeletedLogs | Remove-Item
    $LogCount = $DeletedLogs.Count
    Write-Host "Cleaned up $LogCount old log file(s)"
    # Append cleanup info to today's log
    $TodayLog = "$LogFolder\$(Get-Date -Format 'yyyy-MM-dd').log"
    Add-Content $TodayLog "[$(Get-Date -Format 'HH:mm:ss')][cleanup] - Cleaned up $LogCount old log file(s)"
}