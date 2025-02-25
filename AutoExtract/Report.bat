@echo off
TITLE DMARC Report
Color B
cls
Echo.

:: Set the 'folder' variable to the 'dmarc_reports' directory within the script's directory
set "folder=%~dp0dmarc_reports"

:: Extract all ZIP files
for %%F in ("%folder%\*.zip") do (
    powershell -Command "Expand-Archive -Path '%%F' -DestinationPath '%folder%\%%~nF' -Force"
)

:: Extract all GZ files and replace the .gz extension with .xml
for %%F in ("%folder%\*.gz") do (
    powershell -Command "try { $gzipFile='%%F'; $destinationFile = $gzipFile -replace '\.gz$', '.xml'; $fs=[System.IO.File]::OpenRead($gzipFile); $gs=New-Object System.IO.Compression.GZipStream($fs, [System.IO.Compression.CompressionMode]::Decompress); $out=[System.IO.File]::Create($destinationFile); $buffer=New-Object byte[] 4096; while (($read = $gs.Read($buffer, 0, $buffer.Length)) -gt 0) { $out.Write($buffer, 0, $read) }; $gs.Close(); $fs.Close(); $out.Close() } catch { Write-Host 'Error extracting gz' }"
)

:: Delete ZIP files after extraction
del "%folder%\*.zip"

:: Delete GZ files after extraction
del "%folder%\*.gz"

echo Extraction completed.
Echo.
Echo Generating DMARC report...
python.exe REPORT_Full.py "Customer name"

:: Wait for 3 seconds and delete all processed reports
timeout /t 3
powershell -Command "Remove-Item -Path '%folder%\*' -Recurse -Force"
exit 0
