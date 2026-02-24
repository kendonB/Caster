@echo off
echo Running WRS from Dragonfly CLI.

SetLocal DisableDelayedExpansion
set "currentpath=%~dp0"
set "wsr_python_metadata=%currentpath%castervoice\bin\data\wsr_python_path.txt"
set "runtime_python="

TITLE Caster: Status Window
if exist "%wsr_python_metadata%" (
    for /f "usebackq delims=" %%i in ("%wsr_python_metadata%") do if not defined runtime_python set "runtime_python=%%i"
)

if not defined runtime_python goto :fallback_py
if not exist "%runtime_python%" goto :invalid_runtime_python

echo Using WSR interpreter: %runtime_python%
"%runtime_python%" -m dragonfly load --engine sapi5inproc _*.py --no-recobs-messages
goto :after_run

:invalid_runtime_python
echo WARNING: Stored WSR interpreter path is invalid: %runtime_python%

:fallback_py
where py >nul 2>nul
if errorlevel 1 (
    echo ERROR: No valid WSR interpreter metadata and no 'py' launcher found.
    echo Run Install_Caster_WSR.bat first to configure the runtime interpreter.
    goto :after_run
)

echo NOTICE: Falling back to default py launcher interpreter.
py -m dragonfly load --engine sapi5inproc _*.py --no-recobs-messages

:after_run
pause 1
