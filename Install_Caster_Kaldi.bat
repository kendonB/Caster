@echo off

SetLocal DisableDelayedExpansion
set "currentpath=%~dp0"
for %%I in ("%currentpath%.") do set "repo_root=%%~fI"
set "kaldi_legacy_python_metadata=%currentpath%castervoice\bin\data\kaldi_python_path.txt"
set "venv_dir=%currentpath%.venv"
set "runtime_python=%venv_dir%\Scripts\python.exe"
set "python_request=3.12"
set "installer_requirements=%currentpath%requirements-windows-installer.txt"
set "kaldi_wheel_resolver=%currentpath%castervoice\lib\kaldi_wheel.py"
set "kaldi_model_installer=%currentpath%castervoice\lib\kaldi_model.py"
set "kaldi_install_source="
set "kaldi_engine_version="
set "kaldi_model_status=not-installed"
set "pronunciation_backend_status=not-installed"
set "nltk_data_dir=%venv_dir%\nltk_data"
set "qt_arch_supported=0"
set "local_dragonfly_distribution="
set "kaldi_requirement_distribution="
set "local_dragonfly_source_url="
set "kaldi_requirement_warning="
set "kaldi_resolver_failed="

echo Installation path: %currentpath%
echo Installing Caster dependencies for Kaldi using the local uv virtualenv.

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

echo Upgrading pip for Kaldi interpreter...
uv pip install --python "%runtime_python%" --upgrade pip
if errorlevel 1 (
    echo ERROR: Failed while upgrading pip for Kaldi interpreter.
    exit /b 3
)

if not exist "%installer_requirements%" (
    echo ERROR: Installer requirements file not found at %installer_requirements%.
    exit /b 4
)

echo Installing Caster dependencies for Kaldi...
uv pip install --python "%runtime_python%" -r "%installer_requirements%"
if errorlevel 1 (
    echo ERROR: Failed while installing dependencies from %installer_requirements%.
    exit /b 4
)

if not exist "%kaldi_wheel_resolver%" (
    echo ERROR: Kaldi wheel resolver not found at %kaldi_wheel_resolver%.
    exit /b 4
)

set "local_dragonfly_probe=%TEMP%\caster_local_dragonfly_%RANDOM%.txt"
"%runtime_python%" "%kaldi_wheel_resolver%" --detect-local-source-dragonfly > "%local_dragonfly_probe%"
if errorlevel 1 (
    if exist "%local_dragonfly_probe%" del /q "%local_dragonfly_probe%" >nul 2>nul
    echo ERROR: Failed while checking for a local dragonfly source install.
    exit /b 4
)
for /f "usebackq tokens=1,* delims==" %%A in ("%local_dragonfly_probe%") do (
    if /i "%%A"=="local_dragonfly_distribution" set "local_dragonfly_distribution=%%B"
    if /i "%%A"=="local_dragonfly_source_url" set "local_dragonfly_source_url=%%B"
)
if exist "%local_dragonfly_probe%" del /q "%local_dragonfly_probe%" >nul 2>nul

if defined local_dragonfly_source_url (
    echo WARNING: Local dragonfly source install detected in %venv_dir%.
    echo WARNING: Leaving it unchanged and using its compatibility metadata for Kaldi resolution.
) else (
    echo Installing Dragonfly runtime dependency...
    uv pip install --python "%runtime_python%" "dragonfly2>=0.34.0"
    if errorlevel 1 (
        echo ERROR: Failed while installing dragonfly2.
        exit /b 4
    )
)

set "kaldi_wheel_info=%TEMP%\caster_kaldi_wheel_%RANDOM%.txt"
"%runtime_python%" "%kaldi_wheel_resolver%" > "%kaldi_wheel_info%"
if errorlevel 1 (
    set "kaldi_resolver_failed=1"
)

for /f "usebackq tokens=1,* delims==" %%A in ("%kaldi_wheel_info%") do (
    if /i "%%A"=="tag_name" set "kaldi_release_tag=%%B"
    if /i "%%A"=="asset_name" set "kaldi_wheel_asset=%%B"
    if /i "%%A"=="browser_download_url" set "kaldi_wheel_url=%%B"
    if /i "%%A"=="kaldi_requirement_distribution" set "kaldi_requirement_distribution=%%B"
    if /i "%%A"=="local_dragonfly_source_url" set "local_dragonfly_source_url=%%B"
    if /i "%%A"=="kaldi_requirement_warning" set "kaldi_requirement_warning=%%B"
)
if exist "%kaldi_wheel_info%" del /q "%kaldi_wheel_info%" >nul 2>nul

if defined kaldi_resolver_failed (
    echo NOTICE: Unable to resolve the latest Dragonfly-compatible GitHub Kaldi wheel.
    goto :install_kaldi_fallback
)

if not defined kaldi_wheel_url (
    echo NOTICE: Dragonfly-compatible GitHub Kaldi wheel metadata was incomplete.
    goto :install_kaldi_fallback
)

if defined kaldi_requirement_warning echo WARNING: %kaldi_requirement_warning%

echo Installing Kaldi engine support dependencies...
uv pip install --upgrade --python "%runtime_python%" "sounddevice==0.3.*" "webrtcvad-wheels==2.0.*"
if errorlevel 1 (
    echo NOTICE: Failed while installing Kaldi support dependencies for the GitHub wheel path.
    goto :install_kaldi_fallback
)

echo Installing Kaldi engine from GitHub release %kaldi_release_tag%...
echo Selected wheel: %kaldi_wheel_asset%
uv pip install --upgrade --python "%runtime_python%" "%kaldi_wheel_url%"
if errorlevel 1 (
    echo NOTICE: Failed while installing the GitHub Kaldi wheel.
    goto :install_kaldi_fallback
)

set "kaldi_version_file=%TEMP%\caster_kaldi_version_%RANDOM%.txt"
"%runtime_python%" -c "import importlib.metadata as md; print(md.version('kaldi-active-grammar'))" > "%kaldi_version_file%"
if errorlevel 1 (
    if exist "%kaldi_version_file%" del /q "%kaldi_version_file%" >nul 2>nul
    echo NOTICE: Installed GitHub Kaldi wheel could not be verified.
    goto :install_kaldi_fallback
)
set /p kaldi_engine_version=<"%kaldi_version_file%"
if exist "%kaldi_version_file%" del /q "%kaldi_version_file%" >nul 2>nul
set "kaldi_install_source=github-wheel"
goto :after_kaldi_install

:install_kaldi_fallback
if /i "%kaldi_requirement_distribution%"=="dragonfly" goto :local_dragonfly_kaldi_failure
if not defined kaldi_requirement_distribution if /i "%local_dragonfly_distribution%"=="dragonfly" goto :local_dragonfly_kaldi_failure
echo Installing Kaldi engine dependencies via uv package fallback...
uv pip install --upgrade --python "%runtime_python%" "dragonfly2[kaldi]"
if errorlevel 1 (
    echo ERROR: Failed while installing dragonfly2[kaldi].
    exit /b 5
)
set "kaldi_version_file=%TEMP%\caster_kaldi_version_%RANDOM%.txt"
"%runtime_python%" -c "import importlib.metadata as md; print(md.version('kaldi-active-grammar'))" > "%kaldi_version_file%"
if errorlevel 1 (
    if exist "%kaldi_version_file%" del /q "%kaldi_version_file%" >nul 2>nul
    echo ERROR: Failed while verifying the fallback Kaldi package installation.
    exit /b 5
)
set /p kaldi_engine_version=<"%kaldi_version_file%"
if exist "%kaldi_version_file%" del /q "%kaldi_version_file%" >nul 2>nul
set "kaldi_install_source=package-fallback"
goto :after_kaldi_install

:local_dragonfly_kaldi_failure
echo ERROR: Local dragonfly compatibility metadata was detected, but the matching GitHub Kaldi wheel path did not complete successfully.
echo ERROR: Aborting instead of falling back to dragonfly2[kaldi], which may install an incompatible Kaldi stack.
if defined local_dragonfly_source_url echo ERROR: Local dragonfly source: %local_dragonfly_source_url%
exit /b 5

:after_kaldi_install
if not defined kaldi_engine_version set "kaldi_engine_version=unknown"
echo Installed kaldi-active-grammar version: %kaldi_engine_version%
echo Kaldi install source: %kaldi_install_source%

echo Installing Kaldi pronunciation generation dependencies...
uv pip install --upgrade --python "%runtime_python%" "g2p_en>=2.1.0"
if errorlevel 1 (
    echo WARNING: Failed while installing g2p_en for local pronunciation generation.
    echo WARNING: Unknown-word auto-pronunciation may be unavailable until g2p_en is installed manually.
    set "pronunciation_backend_status=failed"
    goto :after_pronunciation_backend
)

if not exist "%nltk_data_dir%" mkdir "%nltk_data_dir%" >nul 2>nul
set "nltk_bootstrap_script=%TEMP%\caster_kaldi_nltk_%RANDOM%.py"
> "%nltk_bootstrap_script%" echo import os, sys
>> "%nltk_bootstrap_script%" echo import nltk
>> "%nltk_bootstrap_script%" echo nltk_data_dir = os.path.abspath(sys.argv[1])
>> "%nltk_bootstrap_script%" echo os.makedirs(nltk_data_dir, exist_ok=True)
>> "%nltk_bootstrap_script%" echo missing = []
>> "%nltk_bootstrap_script%" echo for package in ["cmudict", "averaged_perceptron_tagger"]:
>> "%nltk_bootstrap_script%" echo     if not nltk.download(package, download_dir=nltk_data_dir, quiet=True):
>> "%nltk_bootstrap_script%" echo         missing.append(package)
>> "%nltk_bootstrap_script%" echo for package in ["averaged_perceptron_tagger_eng"]:
>> "%nltk_bootstrap_script%" echo     nltk.download(package, download_dir=nltk_data_dir, quiet=True)
>> "%nltk_bootstrap_script%" echo if missing:
>> "%nltk_bootstrap_script%" echo     raise SystemExit("Failed to download required NLTK data: " + ", ".join(missing))
"%runtime_python%" "%nltk_bootstrap_script%" "%nltk_data_dir%"
set "nltk_bootstrap_exit=%ERRORLEVEL%"
if exist "%nltk_bootstrap_script%" del /q "%nltk_bootstrap_script%" >nul 2>nul
if not "%nltk_bootstrap_exit%"=="0" (
    echo WARNING: Failed while downloading required NLTK data for g2p_en.
    echo WARNING: Unknown-word auto-pronunciation may be unavailable until the NLTK data is restored.
    set "pronunciation_backend_status=failed"
    goto :after_pronunciation_backend
)

set "g2p_verify_script=%TEMP%\caster_kaldi_g2p_%RANDOM%.py"
> "%g2p_verify_script%" echo import os, sys
>> "%g2p_verify_script%" echo os.environ["NLTK_DATA"] = os.path.abspath(sys.argv[1])
>> "%g2p_verify_script%" echo from g2p_en import G2p
>> "%g2p_verify_script%" echo phones = G2p()("sikuli")
>> "%g2p_verify_script%" echo if not phones:
>> "%g2p_verify_script%" echo     raise SystemExit("g2p_en returned no phones")
"%runtime_python%" "%g2p_verify_script%" "%nltk_data_dir%"
set "g2p_verify_exit=%ERRORLEVEL%"
if exist "%g2p_verify_script%" del /q "%g2p_verify_script%" >nul 2>nul
if not "%g2p_verify_exit%"=="0" (
    echo WARNING: g2p_en was installed, but pronunciation generation could not be verified.
    echo WARNING: Unknown-word auto-pronunciation may still be unavailable until the local NLTK data is fixed.
    set "pronunciation_backend_status=failed"
    goto :after_pronunciation_backend
)

set "pronunciation_backend_status=installed"
echo Kaldi pronunciation generation backend installed.

:after_pronunciation_backend

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

if "%py_bits%"=="64" (
    set "qt_arch_supported=1"
    goto :install_qt
)
if "%py_bits%"=="32" goto :skip_qt_32
goto :skip_qt_other

:install_qt
echo Installing Qt bindings for Kaldi UI features...
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

echo.
if not exist "%kaldi_model_installer%" (
    echo NOTICE: Kaldi model helper not found at %kaldi_model_installer%.
    set "kaldi_model_status=helper-missing"
    goto :after_model
)

choice /c YN /n /m "Download a Kaldi model now? [Y]es [N]o: "
if errorlevel 2 goto :skip_model_download

"%runtime_python%" "%kaldi_model_installer%" --repo-root "%repo_root%"
set "kaldi_model_exit=%ERRORLEVEL%"
if "%kaldi_model_exit%"=="0" (
    set "kaldi_model_status=installed"
    goto :after_model
)
if "%kaldi_model_exit%"=="2" (
    set "kaldi_model_status=skipped"
    goto :after_model
)
echo WARNING: Failed while downloading or installing a Kaldi model.
echo WARNING: You can rerun Install_Caster_Kaldi.bat later to download one.
set "kaldi_model_status=failed"
goto :after_model

:skip_model_download
set "kaldi_model_status=skipped"

:after_model

if exist "%kaldi_legacy_python_metadata%" del /q "%kaldi_legacy_python_metadata%" >nul 2>nul
goto :install_complete

:install_complete

echo.
echo Kaldi dependency installation completed successfully.
echo Kaldi virtualenv: %venv_dir%
echo Kaldi runtime interpreter: %runtime_python%
if "%pronunciation_backend_status%"=="installed" echo Kaldi pronunciation data: %nltk_data_dir%
if "%pronunciation_backend_status%"=="failed" echo WARNING: Kaldi pronunciation generation is not fully installed. Unknown words may require manual user_lexicon entries.
if "%kaldi_model_status%"=="installed" echo Kaldi model directory: %repo_root%\kaldi_model
if "%kaldi_model_status%"=="skipped" echo Kaldi model download skipped. Run Install_Caster_Kaldi.bat later if you want the guided model download.
if "%kaldi_model_status%"=="failed" echo Kaldi model install failed. Download a model later or rerun Install_Caster_Kaldi.bat.
if "%kaldi_model_status%"=="helper-missing" echo Kaldi model helper is unavailable. Download a model manually from the upstream releases page.
if not "%qt_arch_supported%"=="1" echo NOTE: Qt-based UI features require a supported 64-bit Python architecture.
if not "%kaldi_model_status%"=="installed" echo See Caster Kaldi install instructions on ReadTheDocs.
echo Next step: run Run_Caster_Kaldi.bat
pause 1
