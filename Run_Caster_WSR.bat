@echo off
echo Running WSR from Dragonfly CLI.

SetLocal DisableDelayedExpansion
set "currentpath=%~dp0"
set "runtime_python=%currentpath%.venv\Scripts\python.exe"

TITLE Caster: Status Window
if not exist "%runtime_python%" goto :missing_runtime_python

echo Using WSR interpreter: %runtime_python%
"%runtime_python%" -m dragonfly load --engine sapi5inproc _*.py --no-recobs-messages
goto :after_run

:missing_runtime_python
echo ERROR: Local Caster virtualenv is missing: %runtime_python%
echo Run Install_Caster_WSR.bat first to create .venv and install dependencies.

:after_run
pause 1
