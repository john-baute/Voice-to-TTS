# Voice-to-TTS

A project to turn someone's voice to text (transcription) and route audio between virtual devices.

This README documents how to set up the project on Windows, create and activate the Python virtual environment used by the repository, install Vosk and other dependencies, download and extract a Vosk model, and run the real-time microphone transcription script (`transcription.py`). It also includes a few troubleshooting tips so contributors can reproduce the environment.

## Prerequisites
- Windows 10/11 (PowerShell)
- Python 3.8+ installed and available on PATH
- (Optional) Administrator privileges to install system-wide tools or drivers

## Quick setup (PowerShell)
Open PowerShell and run the commands from the project root (where this `README.md` lives).

1) Create and activate the venv

```powershell
# create the venv (only if not present)
python -m venv venv

# Activate the venv for the current PowerShell session - dot-source the Activate.ps1
. .\venv\Scripts\Activate.ps1

# If Activation is blocked by execution policy, either run this once to allow scripts for your user:
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force

# OR open a new PowerShell with a one-off bypass (non-persistent):
# Start-Process -FilePath powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -NoExit -Command `. '$(Resolve-Path .\venv\Scripts\Activate.ps1')'`" -WorkingDirectory (Get-Location)
```

2) Upgrade pip and install Python dependencies

```powershell
# install required packages in the activated venv
python -m pip install --upgrade pip
python -m pip install vosk sounddevice
```

3) Download and extract a Vosk model (small model recommended for CPU realtime)

```powershell
# download (example: small English model)
Invoke-WebRequest -Uri "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip" -OutFile "vosk-model-small-en-us.zip"

# extract into a folder in the project root
Expand-Archive -Path "vosk-model-small-en-us.zip" -DestinationPath ".\vosk-model-small-en-us"

# optional: remove the zip to save space
Remove-Item .\vosk-model-small-en-us.zip
```

Notes:
- The script `transcription.py` will try to auto-detect a model folder inside the project. If you extracted to a folder with a different name, pass its path with `--model` when running the script.

## Run the transcription script

From the activated venv, run:

```powershell
# list available sound devices and their indices (useful to find your microphone or a virtual cable)
python transcription.py --list-devices

# start realtime transcription (writes final transcripts to transcripts.txt in the project root)
python transcription.py

# if you need to explicitly specify a model folder or device index:
python transcription.py --model .\vosk-model-small-en-us --device 2
```

The script prints partial results to the console and appends final results (timestamped) to `transcripts.txt` in the current working directory.

## Troubleshooting

- Activation blocked: If PowerShell refuses to run `Activate.ps1` with a SecurityError about execution policies, either set a per-user policy once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

- Or use a one-off bypass when opening a new shell (see above). If Group Policy enforces a policy (MachinePolicy/UserPolicy present), you cannot override it; use the bypass Start-Process approach instead.

- Model not found / failed to load: If you see an error like `Folder 'vosk-model-small-en-us' does not contain model files`, ensure you extracted the zip and pointed `--model` to the extracted folder (the folder should contain files/folders like `am/`, `model.conf`, or `final.mdl`).

- Device selection: Use `python transcription.py --list-devices` to get the list of sound devices and their indices. If you have virtual cables (VB‑Audio) or multiple microphones, pass the device index with `--device N`.

- If `sounddevice` can't open the device, double-check sample rate compatibility and try matching the `--samplerate` argument (default 16000) to your device or let `sounddevice` resample.
