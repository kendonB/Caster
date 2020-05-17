@echo off
echo Runnig Kaldi from Dragonfly CLI

set currentpath=%~dp0

TITLE Caster: Status Window
C:\Python27\python.exe -m dragonfly load _*.py --engine kaldi  --no-recobs-messages

pause 1
