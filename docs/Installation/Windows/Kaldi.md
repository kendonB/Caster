# Kaldi - Classic Install

Caster currently supports Kaldi on Microsoft Windows 10 through Windows 11. Consider supporting the author [daanzu](https://github.com/sponsors/daanzu) if you use his engine full-time.

## 1. Prerequisites

- Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and ensure `uv` is available on `PATH`.
- `Install_Caster_Kaldi.bat` creates or updates the repo-local `.venv` with uv-managed CPython `3.12`.
   - If uv has not installed Python `3.12` yet, run `uv python install 3.12` and rerun the installer.
   - The Kaldi installer is validated for 64-bit Windows Python in that uv-managed `.venv`.

## 2. Caster

1. Download Caster from the [master branch](https://github.com/dictation-toolbox/Caster/archive/master.zip).
2. Open the downloaded zip file.
3. Copy the contents of the `Caster-master` folder. You can put it anywhere, but `%USERPROFILE%\Documents\Caster` is common.
4. *Optional step* for Caster's `Legion` MouseGrid on Windows 8 and above.
   - The Legion MouseGrid requires [Microsoft Visual C++ Redistributable Packages for Visual Studio 2015, 2017 and 2019 (x86).](https://support.microsoft.com/en-nz/help/2977003/the-latest-supported-visual-c-downloads) This should not be needed if Windows 10 or Windows 11 is up to date.
5. Click `Install_Caster_Kaldi.bat` to install prerequisite Caster dependencies for Kaldi.
   - The installer creates or updates `.\.venv` with uv-managed CPython `3.12` and installs dependencies into that local virtual environment.
   - The installer tries to resolve the latest `kaldi-active-grammar` GitHub wheel compatible with the Dragonfly distribution installed in `.\.venv`.
   - If a local `dragonfly` source-directory install is already present in `.\.venv`, the installer preserves it, uses its Kaldi compatibility metadata, and does not replace it with `dragonfly2`.
   - On the default `dragonfly2` path, the installer falls back to `dragonfly2[kaldi]` if GitHub lookup or wheel installation fails.
   - If a preserved local `dragonfly` source install does not have a compatible Kaldi path, the installer stops with an error instead of overwriting it.
   - The installer can optionally download and extract a Kaldi model into `.\kaldi_model` for you.

## 3. Set Up Kaldi Model

1. When prompted by `Install_Caster_Kaldi.bat`, choose whether to download a Kaldi model now.
   - The guided installer currently offers:
     - `medium` as the recommended balanced choice
     - `small` for a smaller download
     - `big` for the largest model
2. If you skip the guided download, download your preferred Kaldi model from [kaldi-active-grammar/releases](https://github.com/daanzu/kaldi-active-grammar/releases).
   - Current model downloads are linked from the upstream `docs/models.md` page and may come from an older release tag than the latest engine wheel release.
3. Extract `kaldi_model_<Model Type>.zip` to `%USERPROFILE%\Documents\Caster`.

## 4. Launch Caster (Kaldi) for Classic Install

1. Go to `%USERPROFILE%\Documents\Caster`.
2. Double-click `Run_Caster_Kaldi.bat`.

**Note:** Kaldi is a flexible engine which can be configured via engine parameters to customize your experience.

- `Run_Caster_Kaldi.bat` launches `dragonfly` with `--engine kaldi --no-recobs-messages --engine-options "model_dir=kaldi_model, vad_padding_end_ms=300"` using `.\.venv\Scripts\python.exe`.
- `Run_Caster_Kaldi.bat` also honors `CASTER_KALDI_AUDIO_INPUT_DEVICE` for pinning a specific PortAudio input device and `CASTER_KALDI_ENGINE_OPTIONS` for appending extra engine options without editing the batch file.
- See the list of Kaldi [engine parameters](https://dragonfly2.readthedocs.io/en/latest/kaldi_engine.html#engine-configuration) for additional configuration options.

### Update Caster

1. Backup `%USERPROFILE%\Documents\Caster`.
2. Delete `%USERPROFILE%\Documents\Caster`.
3. Repeat Steps `1. - 5.` within the Caster install section.

------

### Troubleshooting Kaldi

- Receive an error that `uv` is not recognized.

   > fix: install uv from https://docs.astral.sh/uv/getting-started/installation/ and restart your shell.

- Receive an error that uv-managed Python `3.12` could not be created for `.\.venv`.

   > fix: run `uv python install 3.12`, then rerun `Install_Caster_Kaldi.bat`.

- Receive a notice that the latest GitHub Kaldi wheel could not be resolved or installed.

   > fix: if the installer is managing `dragonfly2`, it will automatically fall back to `dragonfly2[kaldi]`. If it detected a local `dragonfly` source install in `.\.venv`, it will stop instead so that install is not overwritten.

- Skip the model download during install, or the guided model download fails.

   > fix: rerun `Install_Caster_Kaldi.bat` to use the guided model installer again, or download a model manually from the upstream releases page and extract it to `.\kaldi_model`.

- Receive a message that Qt dependencies were skipped or PySide6 failed to install.

   > This happens on unsupported architectures or when no compatible PySide6 wheel is available for the installer-created uv-managed Windows x64 `.venv`. Core Kaldi grammar functionality can still run, but HUD/settings-window features requiring Qt are unavailable.

- Receive an error about a missing or invalid Kaldi runtime interpreter in `Run_Caster_Kaldi.bat`.

   > fix: rerun `Install_Caster_Kaldi.bat` to recreate `.\.venv` with uv-managed Python and restore `.\.venv\Scripts\python.exe`.

- See repeated `no good block received recently, so reconnecting audio` warnings while Kaldi is listening.

   > This means the audio backend is opening a device successfully but not receiving enough valid 10 ms microphone blocks to keep streaming. On Windows this is often the default `MME` input for a Bluetooth headset.
   >
   > fix:
   >
   > 1. List the PortAudio input devices:
   >    `.\.venv\Scripts\python.exe -c "from dragonfly.engines.backend_kaldi.engine import KaldiEngine; KaldiEngine.print_mic_list()"`
   > 2. Pick a more stable device entry for the same microphone, usually `Windows WASAPI`.
   > 3. Launch Caster with that exact device name, for example in PowerShell:
   >    `$env:CASTER_KALDI_AUDIO_INPUT_DEVICE = "Headset (Example Device), Windows WASAPI"`
   >    `.\Run_Caster_Kaldi.bat`
   >
   > You can also pass a numeric PortAudio device index instead of the full device name by setting `CASTER_KALDI_AUDIO_INPUT_DEVICE` to that index.

**Known Issues**

- Kaldi outputs a lot of text to the Caster status window on Windows.
  - [Kaldi mitigation for keyboard action processing bug via debug mode](https://github.com/dictation-toolbox/Caster/issues/799)
