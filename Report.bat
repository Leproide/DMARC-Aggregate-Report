@echo off
TITLE DMARC Report
:start
Color B
cls
Echo.
Echo Press any key to generate the report...
pause > nul
python.exe REPORT_Full.py "Test S.r.l"
cls
echo.
color A
echo Report generated!
timeout /t 2 > nul
goto start
