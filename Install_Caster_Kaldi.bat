@echo off
set currentpath=%~dp0
echo Installation path: %currentpath%
echo Using this python/pip:
python -m pip -V

echo Installing Caster Dependencies
py -m pip install -r "%currentpath%requirements.txt"
py -m pip install dragonfly2[kaldi]

echo Installing optional Qt bindings for HUD/settings UI features (best effort)
py -m pip install --only-binary=:all: "PySide6>=6.6"
if errorlevel 1 (
    echo NOTICE: PySide6 wheel unavailable for this interpreter; trying PySide2.
    py -m pip install --only-binary=:all: "PySide2>=5.14"
    if errorlevel 1 (
        echo NOTICE: No compatible Qt wheel found for this interpreter.
        echo NOTICE: Core Kaldi grammar functionality can still run.
        echo NOTICE: HUD/settings-window features requiring Qt may be unavailable.
        cmd /c exit /b 0
    )
)

echo Remember: Manually install kaldi a model. 
echo See Caster kaldi install instructions on ReadTheDocs.

pause 1
