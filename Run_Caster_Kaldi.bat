@echo off
echo Running Kaldi from Dragonfly CLI.

SetLocal DisableDelayedExpansion
set "currentpath=%~dp0"
set "runtime_python=%currentpath%.venv\Scripts\python.exe"
set "nltk_data_dir=%currentpath%.venv\nltk_data"

TITLE Caster: Status Window
if not exist "%runtime_python%" goto :missing_runtime_python

set "caster_user_dir="
for /f "usebackq delims=" %%I in (`"%runtime_python%" -c "from castervoice.lib.settings import detected_user_dir; print(detected_user_dir())" 2^>nul`) do if not defined caster_user_dir set "caster_user_dir=%%I"

echo Using Kaldi interpreter: %runtime_python%
if defined caster_user_dir echo Detected Caster user directory: %caster_user_dir%
if exist "%nltk_data_dir%" (
    set "NLTK_DATA=%nltk_data_dir%"
    echo Using Kaldi pronunciation data: %nltk_data_dir%
)
"%runtime_python%" -m dragonfly load _*.py --engine kaldi --no-recobs-messages --engine-options "model_dir=kaldi_model, vad_padding_end_ms=300"
goto :after_run

:missing_runtime_python
echo ERROR: Local Caster virtualenv is missing: %runtime_python%
echo Run Install_Caster_Kaldi.bat first to create .venv and install dependencies.

:after_run
pause 1
