# Tạo backup cho các file đã sửa
Get-ChildItem -Path . -Recurse -File | ForEach-Object {
    if ($_.LastWriteTime -gt (Get-Date).AddMinutes(-5)) {
        Copy-Item $_.FullName "$($_.FullName).backup"
    }
}

# Khởi động lại server
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Start-Process python -ArgumentList "app.py" 