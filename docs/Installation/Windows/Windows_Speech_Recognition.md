# Windows Speech Recognition - Classic Install

Caster currently supports Windows Speech Recognition (WSR) on Microsoft Windows 7 through Windows 10.

## 1. Prerequisites

- Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and ensure `uv` is available on `PATH`.
- `Install_Caster_WSR.bat` creates or updates the repo-local `.venv` with uv-managed CPython `3.12`.
   - If uv has not installed Python `3.12` yet, run `uv python install 3.12` and rerun the installer.
   - The WSR installer is validated for 64-bit Windows Python in that uv-managed `.venv`.

## 2. Caster

   1. Download Caster from the [master branch](https://github.com/dictation-toolbox/Caster/archive/master.zip).
   2. Open up the zip file downloaded
   3. Copy the contents of `Caster-master` folder, you can put it anywhere but it is common to use `%USERPROFILE%\Documents\Caster`.
   4. *Optional Step* for Caster's`Legion` MouseGrid - Legion Feature available on Windows 8 and above
         - The Legion MouseGrid requires [Microsoft Visual C++ Redistributable Packages for Visual Studio 2015, 2017 and 2019 (x86).](https://support.microsoft.com/en-nz/help/2977003/the-latest-supported-visual-c-downloads) Note: Should not be needed if Windows 10 is up-to-date.
   5. Click `Install_Caster_WSR.bat` to install prerequisite Caster dependencies for WSR.
       - The installer creates or updates `.\.venv` with uv-managed CPython `3.12` and installs dependencies into that local virtual environment.
       - If a local `dragonfly` source-directory install is already present in `.\.venv`, the installer preserves it instead of replacing it with `dragonfly2`.

## 3. Launch Caster for Classic Install

   1. Go to  `%USERPROFILE%\Documents\Caster`

   2. Start Caster by double clicking on `Run_Caster_WSR.bat`.

   3. To test, open Windows Notepad and try saying `arch brov char delta` producing `abcd` text. Setup complete!

## Update Caster

   1. Backup `%USERPROFILE%\Documents\Caster`
   2. Delete `%USERPROFILE%\Documents\Caster`
   3. Repeat Steps `1. - 3.` within the Caster install section

------

### Troubleshooting Windows Speech Recognition

- Receive an error that `uv` is not recognized.

   > fix: install uv from https://docs.astral.sh/uv/getting-started/installation/ and restart your shell.

- Receive an error that uv-managed Python `3.12` could not be created for `.\.venv`.

   > fix: run `uv python install 3.12`, then rerun `Install_Caster_WSR.bat`.

- Receive a message that Qt dependencies were skipped.

   > This happens on unsupported architectures or when no compatible PySide6 wheel is available for the installer-created uv-managed Windows x64 `.venv`. Core WSR grammar functionality can still run, but HUD/settings-window features requiring Qt are unavailable.

- Receive an error about a missing or invalid WSR runtime interpreter in `Run_Caster_WSR.bat`.

   > fix: rerun `Install_Caster_WSR.bat` to recreate `.\.venv` with uv-managed Python and restore `.\.venv\Scripts\python.exe`.

- Receive the `-2147352567` COM error when Caster starts. This is most likely related to the microphone being utilized by another program. See [issue #821](https://github.com/dictation-toolbox/Caster/issues/821) and [#68](https://github.com/dictation-toolbox/Caster/issues/68).  This can be mitigated by closing the program that's utilizing the microphone.

   > com_error: (-2147352567, 'Exception occurred.', (0, None, None, None, 0, -2004287480), None)`

- Receive the `'win32com.gen_py' has no attribute 'CLSIDToClassMap'` COM error when Caster starts. 

      > WARNING:engine:Exception while initializing sapi5 engine: module 'win32com.gen_py.C866CA3A-32F7-11D2-9602-00C04F8EE628x0x5x4' has no attribute 'CLSIDToClassMap'
      > ERROR:command:Exception while initializing sapi5 engine: module 'win32com.gen_py.C866CA3A-32F7-11D2-9602-00C04F8EE628x0x5x4' has no attribute 'CLSIDToClassMap

   > fix: run `Remove-Item -path $env:LOCALAPPDATA\Temp\gen_py -recurse` in powershell
