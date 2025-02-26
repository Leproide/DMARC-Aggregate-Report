# Set folder path
$folder = "dmarc_reports"

# Create title and clear screen
Write-Host "DMARC Report" -ForegroundColor Cyan
Clear-Host

# Extract all ZIP files
Get-ChildItem -Path $folder -Filter "*.zip" | ForEach-Object {
    Expand-Archive -Path $_.FullName -DestinationPath "$folder\$($_.BaseName)" -Force
}

# Extract all GZ files and convert to XML
Get-ChildItem -Path $folder -Filter "*.gz" | ForEach-Object {
    try {
        $gzipFile = $_.FullName
        $destinationFile = $gzipFile -replace '\.gz$', '.xml'
        Write-Host "Extracting: $gzipFile -> $destinationFile"

        $fs = [System.IO.File]::OpenRead($gzipFile)
        $gs = New-Object System.IO.Compression.GZipStream($fs, [System.IO.Compression.CompressionMode]::Decompress)
        $out = [System.IO.File]::Create($destinationFile)
        $gs.CopyTo($out)

        $gs.Close()
        $fs.Close()
        $out.Close()
    } catch {
        Write-Host "Error extracting gz: $_" -ForegroundColor Red
    }
}

# Delete ZIP files after extraction
Remove-Item -Path "$folder\*.zip" -Force

# Delete GZ files after extraction
Remove-Item -Path "$folder\*.gz" -Force

Write-Host "Extraction completed." -ForegroundColor Green

# Run the Python script to generate the DMARC report
Write-Host "Generating DMARC report..." -ForegroundColor Yellow
Start-Process -FilePath "python.exe" -ArgumentList '"REPORT_Full.py" "Customer Example"' -NoNewWindow -Wait

# Wait 3 seconds before deleting processed reports
Start-Sleep -Seconds 3
Remove-Item -Path "$folder\*" -Recurse -Force

Write-Host "Operation completed." -ForegroundColor Green
