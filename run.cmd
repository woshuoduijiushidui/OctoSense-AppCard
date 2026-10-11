@echo off
setlocal
chcp 65001 >nul
echo Starting Pantry Steward. Please keep this window open.
if not "%~1"=="" goto original_launch
if not exist "%~dp0.local-state\recovery-launch.cmd" goto original_launch
call "%~dp0.local-state\recovery-launch.cmd"
goto launch_finished
:original_launch
python -X utf8 "%~dp0tools\launch.py" %*
:launch_finished
set "pantry_launch_status=%errorlevel%"
if not "%pantry_launch_status%"=="0" (
    echo.
    echo Launch failed. Please share the error messages above.
    pause
)
exit /b %pantry_launch_status%
