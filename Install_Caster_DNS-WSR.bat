
@echo off

SetLocal EnableDelayedExpansion
set python_version=3.10-32
set currentpath=%~dp0
echo Installation path: %currentpath%

@REM execute python launcher for python directory
FOR /F "tokens=1 USEBACKQ delims=" %%i IN (`py -%python_version% -c "import sys; print(sys.exec_prefix)"`) DO ( set python_path=%%i )

@REM  whack a funny trailing character (newline?) from end
set python_path=!python_path:~0,-1!

set PATH=%python_path%;%python_path%/Scripts;%PATH%
echo %PATH%

echo Next line should clearly state python version:
python --version

echo Using this python/pip:

py -%python_version% -m pip install --upgrade pip

echo Installing Caster Dependencies for DNS/WSR
py -%python_version% -m pip install -r "%currentpath%requirements.txt"

echo Installing optional Qt bindings for HUD/settings UI features (best effort)
py -%python_version% -m pip install --only-binary=:all: "PySide6>=6.6"
if errorlevel 1 (
    echo NOTICE: PySide6 wheel unavailable for this interpreter; trying PySide2.
    py -%python_version% -m pip install --only-binary=:all: "PySide2>=5.14"
    if errorlevel 1 (
        echo NOTICE: No compatible Qt wheel found for this interpreter.
        echo NOTICE: Core DNS/WSR grammar functionality can still run.
        echo NOTICE: HUD/settings-window features requiring Qt may be unavailable.
        cmd /c exit /b 0
    )
)

pause 1
