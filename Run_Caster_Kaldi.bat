@echo off
echo Running Kaldi from Dragonfly CLI.

SetLocal EnableDelayedExpansion
set "currentpath=%~dp0"
set "runtime_python=%currentpath%.venv\Scripts\python.exe"
set "nltk_data_dir=%currentpath%.venv\nltk_data"
set "user_dir_probe_file=%TEMP%\caster-user-dir-%RANDOM%%RANDOM%.txt"
set "audio_device_probe_file=%TEMP%\caster-audio-device-%RANDOM%%RANDOM%.txt"
set "configured_audio_input_device=%CASTER_KALDI_AUDIO_INPUT_DEVICE%"
set "configured_engine_options=%CASTER_KALDI_ENGINE_OPTIONS%"

TITLE Caster: Status Window
if not exist "%runtime_python%" goto :missing_runtime_python

set "caster_user_dir=%CASTER_USER_DIR%"
if not defined caster_user_dir (
    "%runtime_python%" -c "from appdirs import user_data_dir; print(user_data_dir(appname='caster', appauthor=False))" > "%user_dir_probe_file%" 2>nul
    if exist "%user_dir_probe_file%" (
        set /p "caster_user_dir="<"%user_dir_probe_file%"
        del "%user_dir_probe_file%" >nul 2>nul
    )
)

echo Using Kaldi interpreter: %runtime_python%
if defined caster_user_dir echo Detected Caster user directory: %caster_user_dir%
if defined caster_user_dir set "CASTER_USER_DIR=%caster_user_dir%"
if exist "%nltk_data_dir%" (
    set "NLTK_DATA=%nltk_data_dir%"
    echo Using Kaldi pronunciation data: %nltk_data_dir%
)
set "kaldi_engine_options=model_dir=kaldi_model, vad_padding_end_ms=300"
if defined configured_audio_input_device (
    "%runtime_python%" -m castervoice.lib.kaldi_audio_device "!configured_audio_input_device!" > "%audio_device_probe_file%"
    if errorlevel 1 goto :invalid_audio_device
    if exist "%audio_device_probe_file%" (
        set /p "resolved_audio_input_device="<"%audio_device_probe_file%"
        del "%audio_device_probe_file%" >nul 2>nul
    )
    set "kaldi_engine_options=!kaldi_engine_options!, audio_input_device=!resolved_audio_input_device!"
    echo Using Kaldi audio input device: !configured_audio_input_device! ^(PortAudio #!resolved_audio_input_device!^)
)
if defined configured_engine_options (
    set "kaldi_engine_options=!kaldi_engine_options!, !configured_engine_options!"
    echo Using extra Kaldi engine options: !configured_engine_options!
)
"%runtime_python%" -m dragonfly load _*.py --engine kaldi --no-recobs-messages --engine-options "!kaldi_engine_options!"
goto :after_run

:missing_runtime_python
echo ERROR: Local Caster virtualenv is missing: %runtime_python%
echo Run Install_Caster_Kaldi.bat first to create .venv and install dependencies.
goto :after_run

:invalid_audio_device
echo ERROR: Could not resolve Kaldi audio input device from CASTER_KALDI_AUDIO_INPUT_DEVICE=!configured_audio_input_device!
if exist "%audio_device_probe_file%" del "%audio_device_probe_file%" >nul 2>nul

:after_run
pause 1
