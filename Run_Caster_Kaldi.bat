@echo off
echo Running Kaldi from Dragonfly CLI

set currentpath=%~dp0

TITLE Caster: Status Window
set CASTER_USER_DIR=C:\Users\KennyBell\Dropbox\caster_windows_user&& python -m dragonfly load _*.py --engine kaldi --no-recobs-messages --engine-options "model_dir=kaldi_model, vad_padding_end_ms=300"


pause 1
