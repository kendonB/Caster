@echo off

SetLocal DisableDelayedExpansion
set "currentpath=%~dp0"
set "wsr_legacy_python_metadata=%currentpath%castervoice\bin\data\wsr_python_path.txt"
set "venv_dir=%currentpath%.venv"
set "runtime_python=%venv_dir%\Scripts\python.exe"
set "python_request=3.12"
set "installer_requirements=%currentpath%requirements-windows-installer.txt"
set "dragonfly_source_probe=%currentpath%castervoice\lib\kaldi_wheel.py"
set "local_dragonfly_source_url="

echo Installation path: %currentpath%
echo Installing Caster dependencies for WSR using the local uv virtualenv.

where uv >nul 2>nul
if errorlevel 1 (
    echo ERROR: uv is required but was not found in PATH.
    echo Install uv first: https://docs.astral.sh/uv/getting-started/installation/
    exit /b 1
)

echo Creating or updating local virtualenv at %venv_dir% with uv-managed Python %python_request%...
uv venv --allow-existing --managed-python --python "%python_request%" "%venv_dir%"
if errorlevel 1 (
    echo ERROR: Unable to create the local .venv with uv-managed Python 3.12.
    echo Run: uv python install 3.12
    exit /b 2
)

if not exist "%runtime_python%" (
    echo ERROR: Failed to resolve the Python interpreter in the local .venv.
    echo Expected: %runtime_python%
    exit /b 6
)

echo Upgrading pip for WSR interpreter...
uv pip install --python "%runtime_python%" --upgrade pip
if errorlevel 1 (
    echo ERROR: Failed while upgrading pip for WSR interpreter.
    exit /b 3
)

if not exist "%installer_requirements%" (
    echo ERROR: Installer requirements file not found at %installer_requirements%.
    exit /b 4
)

echo Installing Caster dependencies for WSR...
uv pip install --python "%runtime_python%" -r "%installer_requirements%"
if errorlevel 1 (
    echo ERROR: Failed while installing dependencies from %installer_requirements%.
    exit /b 4
)

if not exist "%dragonfly_source_probe%" (
    echo ERROR: Dragonfly source detection helper not found at %dragonfly_source_probe%.
    exit /b 4
)

set "local_dragonfly_probe=%TEMP%\caster_local_dragonfly_%RANDOM%.txt"
"%runtime_python%" "%dragonfly_source_probe%" --detect-local-source-dragonfly > "%local_dragonfly_probe%"
if errorlevel 1 (
    if exist "%local_dragonfly_probe%" del /q "%local_dragonfly_probe%" >nul 2>nul
    echo ERROR: Failed while checking for a local dragonfly source install.
    exit /b 4
)
for /f "usebackq tokens=1,* delims==" %%A in ("%local_dragonfly_probe%") do (
    if /i "%%A"=="local_dragonfly_source_url" set "local_dragonfly_source_url=%%B"
)
if exist "%local_dragonfly_probe%" del /q "%local_dragonfly_probe%" >nul 2>nul

if defined local_dragonfly_source_url (
    echo WARNING: Local dragonfly source install detected in %venv_dir%.
    echo WARNING: Leaving it unchanged instead of installing dragonfly2.
) else (
    echo Installing Dragonfly runtime dependency...
    uv pip install --python "%runtime_python%" "dragonfly2>=0.34.0"
    if errorlevel 1 (
        echo ERROR: Failed while installing dragonfly2.
        exit /b 4
    )
)

set "py_bits_file=%TEMP%\caster_py_bits_%RANDOM%.txt"
"%runtime_python%" -c "import struct; print(8*struct.calcsize('P'))" > "%py_bits_file%"
if errorlevel 1 (
    if exist "%py_bits_file%" del /q "%py_bits_file%" >nul 2>nul
    echo ERROR: Failed to determine Python bitness for Qt dependency installation.
    exit /b 7
)
set /p py_bits=<"%py_bits_file%"
if exist "%py_bits_file%" del /q "%py_bits_file%" >nul 2>nul
if not defined py_bits (
    echo ERROR: Failed to determine Python bitness for Qt dependency installation.
    exit /b 7
)

if "%py_bits%"=="64" goto :install_qt
if "%py_bits%"=="32" goto :skip_qt_32
goto :skip_qt_other

:install_qt
echo Installing Qt bindings for WSR UI features...
uv pip install --python "%runtime_python%" --only-binary=:all: "PySide6>=6.6"
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

if exist "%wsr_legacy_python_metadata%" del /q "%wsr_legacy_python_metadata%" >nul 2>nul
goto :install_complete

:install_complete

echo.
echo WSR dependency installation completed successfully.
echo WSR virtualenv: %venv_dir%
echo WSR runtime interpreter: %runtime_python%
echo NOTE: Qt-based UI features require a supported 64-bit Python architecture.
echo Next step: run Run_Caster_WSR.bat
pause 1
