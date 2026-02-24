@echo off

SetLocal DisableDelayedExpansion
set "currentpath=%~dp0"
set "wsr_python_metadata=%currentpath%castervoice\bin\data\wsr_python_path.txt"
set "wsr_python_request=>=3.12"

echo Installation path: %currentpath%
echo Installing Caster dependencies for WSR using uv and Python 3.12+.

where uv >nul 2>nul
if errorlevel 1 (
    echo ERROR: uv is required but was not found in PATH.
    echo Install uv first: https://docs.astral.sh/uv/getting-started/installation/
    exit /b 1
)

echo Validating Python 3.12+ availability through uv...
uv run --python "%wsr_python_request%" -- python --version
if errorlevel 1 (
    echo ERROR: Unable to use Python 3.12+ with uv.
    echo Install Python 3.12+ or run: uv python install 3.12+
    exit /b 2
)

for /f "usebackq delims=" %%i in (`uv run --python "%wsr_python_request%" -- python -c "import sys; print(sys.executable)"`) do set "wsr_python=%%i"
if not defined wsr_python (
    echo ERROR: Failed to resolve the Python interpreter path used for WSR.
    exit /b 6
)
if exist "%wsr_python%" goto :wsr_python_ready
echo ERROR: Resolved WSR Python interpreter does not exist: %wsr_python%
exit /b 6

:wsr_python_ready

echo Upgrading pip for WSR interpreter...
uv pip install --system --python "%wsr_python%" --upgrade pip
if errorlevel 1 (
    echo ERROR: Failed while upgrading pip for WSR interpreter.
    exit /b 3
)

echo Installing Caster dependencies for WSR...
uv pip install --system --python "%wsr_python%" -r "%currentpath%requirements.txt"
if errorlevel 1 (
    echo ERROR: Failed while installing dependencies from requirements.txt.
    exit /b 4
)

for /f "usebackq delims=" %%i in (`uv run --python "%wsr_python%" -- python -c "import struct; print(8*struct.calcsize('P'))"`) do set "py_bits=%%i"
if not defined py_bits (
    echo ERROR: Failed to determine Python bitness for Qt dependency installation.
    exit /b 7
)

if "%py_bits%"=="64" goto :install_qt
if "%py_bits%"=="32" goto :skip_qt_32
goto :skip_qt_other

:install_qt
echo Installing Qt bindings for WSR UI features...
uv pip install --system --python "%wsr_python%" --only-binary=:all: "PySide6>=6.6"
if errorlevel 1 goto :qt_install_failed
goto :after_qt

:qt_install_failed
echo WARNING: Failed while installing PySide6 for Qt-based UI features.
echo WARNING: Continuing install without Qt-based UI features.
cmd /c exit /b 0
goto :after_qt

:skip_qt_32
echo NOTICE: Skipping Qt dependency for detected 32-bit Python.
echo NOTICE: HUD and settings-window features that require Qt may be unavailable.
goto :after_qt

:skip_qt_other
echo NOTICE: Skipping Qt dependency because Python bitness "%py_bits%" is not supported.
echo NOTICE: HUD and settings-window features that require Qt may be unavailable.

:after_qt

for %%d in ("%wsr_python_metadata%") do set "wsr_python_metadata_dir=%%~dpd"
if exist "%wsr_python_metadata_dir%" goto :wsr_metadata_dir_ready
mkdir "%wsr_python_metadata_dir%"
if errorlevel 1 goto :wsr_metadata_dir_create_failed

:wsr_metadata_dir_ready
"%wsr_python%" -c "import os, pathlib; pathlib.Path(os.environ['wsr_python_metadata']).write_text(os.environ['wsr_python'] + '\n', encoding='utf-8')"
if errorlevel 1 goto :wsr_metadata_write_failed
goto :install_complete

:wsr_metadata_dir_create_failed
echo ERROR: Failed to create metadata directory: %wsr_python_metadata_dir%
exit /b 6

:wsr_metadata_write_failed
echo ERROR: Failed to write WSR interpreter metadata: %wsr_python_metadata%
exit /b 6

:install_complete

echo.
echo WSR dependency installation completed successfully.
echo WSR runtime interpreter: %wsr_python%
echo WSR interpreter metadata: %wsr_python_metadata%
echo NOTE: Qt-based UI features require a supported 64-bit Python architecture.
echo Next step: run Run_Caster_WSR.bat
pause 1
