@echo off
set currentpath=%~dp0
echo Installation path: %currentpath%

echo Installing Caster Dependencies
C:\Python27\python.exe -m pip install -r "%currentpath%requirements.txt"
C:\Python27\python.exe -m pip install dragonfly2[kaldi]

echo Remember: Manually install kaldi a model. 
echo See Caster kaldi install instructions on ReadTheDocs.

pause 1
