@echo off
setlocal
chcp 65001 >nul
echo Starting Pantry Steward. Please keep this window open.
python -X utf8 "%~dp0tools\launch.py" %*
set "pantry_launch_status=%errorlevel%"
if not "%pantry_launch_status%"=="0" (
    echo.
    echo Launch failed. Please share the error messages above.
    pause
)
exit /b %pantry_launch_status%
