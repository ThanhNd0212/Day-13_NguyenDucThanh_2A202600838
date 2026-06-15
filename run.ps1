# Đọc các biến trong .env rồi chạy simulator practice với Google Gemini.
# Dùng: nạp key vào .env trước, sau đó chạy:  .\run.ps1

Get-Content "$PSScriptRoot\.env" | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
        $name, $value = $line.Split("=", 2)
        Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
    }
}

Write-Host "Provider endpoint: $env:LOCAL_BASE_URL"
Write-Host "Key bat dau bang: $($env:OPENAI_API_KEY.Substring(0, [Math]::Min(6, $env:OPENAI_API_KEY.Length)))..."

$bin = "$PSScriptRoot\bin\practice\observathon-sim\observathon-sim.exe"
if (-not (Test-Path $bin)) {
    Write-Host "CHUA co binary tai $bin (binary phat hanh theo lich, tai ve truoc)." -ForegroundColor Yellow
    exit 1
}

& $bin --config solution/config.json --wrapper solution/wrapper.py `
    --out run_output.json --concurrency 8
