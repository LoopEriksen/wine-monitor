@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Wine Monitor installer (Windows)

echo.
echo ============================================================
echo  Wine Monitor installer  (Windows)
echo ============================================================
echo.

REM ------------------------------------------------------------------
set "PYCMD="
where py >nul 2>nul && set "PYCMD=py -3"
if not defined PYCMD (
  where python >nul 2>nul && set "PYCMD=python"
)
if not defined PYCMD goto :no_python

%PYCMD% -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
if errorlevel 1 (
  %PYCMD% -c "import sys; print('  Python ' + '.'.join(map(str, sys.version_info[:3])) + ' found, but 3.10 or newer is required.')"
  echo  Install a newer Python from https://www.python.org/downloads/
  echo  (tick "Add python.exe to PATH" in the installer) and run this again.
  pause
  exit /b 1
)
echo == 1/4 Checking Python ==
%PYCMD% -c "import sys; print('  Found Python ' + '.'.join(map(str, sys.version_info[:3])))"

REM ------------------------------------------------------------------
echo.
echo == 2/4 Creating virtual environment (.venv) ==
if not exist ".venv\Scripts\activate.bat" (
  %PYCMD% -m venv .venv
  if errorlevel 1 (
    echo  Could not create .venv. On older Windows installs try:  %PYCMD% -m pip install --user virtualenv
    pause
    exit /b 1
  )
) else (
  echo  .venv already exists - reusing it.
)
.venv\Scripts\python.exe -m pip install --quiet --upgrade pip

REM ------------------------------------------------------------------
echo.
echo == 3/4 Installing Wine Monitor (core + GUI) ==
REM The "hardware" extra (RPi.GPIO) only works on Linux/Pi, so it is not
REM installed here: on Windows the app runs on the built-in simulator, and
REM real sensors live on the Raspberry Pi host (see docs/phase2-companion-windows.md).
.venv\Scripts\python.exe -m pip install --quiet ".[gui]"
if errorlevel 1 (
  echo  pip install failed. Check your internet connection / antivirus, then retry.
  pause
  exit /b 1
)
echo  Installed.

REM ------------------------------------------------------------------
echo.
echo == 4/4 Creating launchers ==
set "WORKDIR=%~dp0"
set "WORKDIR=%WORKDIR:~0,-1%"

REM Double-click launcher (no console window).
> "%~dp0Start Wine Monitor.vbs" echo Set ws = CreateObject("WScript.Shell")
>> "%~dp0Start Wine Monitor.vbs" echo ws.CurrentDirectory = "%~dp0"
>> "%~dp0Start Wine Monitor.vbs" echo ws.Run """%~dp0.venv\Scripts\pythonw.exe"" -m wine_monitor", 0, False
echo  Created: Start Wine Monitor.vbs  (double-click it to run the app)

REM Start Menu shortcut (best effort).
set "PS1=%TEMP%\wm_shortcut_%RANDOM%.ps1"
>  "%PS1%" echo $ws = New-Object -ComObject WScript.Shell
>> "%PS1%" echo $lnk = $ws.CreateShortcut((Join-Path $ws.SpecialFolders('Startup') 'Wine Monitor.lnk'))
>> "%PS1%" echo $lnk.TargetPath = '%WORKDIR%\.venv\Scripts\pythonw.exe'
>> "%PS1%" echo $lnk.Arguments = '-m wine_monitor'
>> "%PS1%" echo $lnk.WorkingDirectory = '%WORKDIR%'
>> "%PS1%" echo $lnk.Description = 'Wine Monitor'
>> "%PS1%" echo $lnk.Save()
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" >nul 2>nul
if errorlevel 1 (
  echo  (Start Menu shortcut not created - no problem, the .vbs launcher works.)
) else (
  echo  Created: Start Menu shortcut "Wine Monitor"
)
del "%PS1%" >nul 2>nul

REM ------------------------------------------------------------------
echo.
echo ============================================================
echo  Done!
echo.
echo   Start the app:
echo     - double-click  "Start Wine Monitor.vbs"  (in this folder), or
echo     - Start Menu   ->  Wine Monitor
echo   Terminal version (shows live readings, no GUI):
echo     .venv\Scripts\wine-monitor.exe --headless
echo   Settings file (edit to change thresholds / email alerts):
echo     wine-monitor.json   (created on first run, in this folder)
echo   Data is stored in:    data\wine_monitor.db
echo.
echo   To remove Wine Monitor: delete this folder (plus the Start Menu
echo   shortcut and "Start Wine Monitor.vbs" if you want them gone).
echo ============================================================
pause
exit /b 0


:no_python
echo  Python was not found on this machine.
echo  Install it from https://www.python.org/downloads/  (3.10 or newer;
echo  tick "Add python.exe to PATH" in the installer), then run this again.
echo.
pause
exit /b 1
