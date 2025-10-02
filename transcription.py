import queue
import sys
import json
import argparse
import os
import sounddevice as sd
from vosk import Model, KaldiRecognizer

DEFAULT_MODEL = "vosk-model-small-en-us"  # folder name you downloaded
SAMPLE_RATE = 16000                        # model-friendly SR
TRANSCRIPTS_DIR = "transcripts"            # folder for transcript files
DEFAULT_OUTFILE = os.path.join(TRANSCRIPTS_DIR, "transcripts.txt")  # default output file
# Removed old DEFAULT_OUTFILE constant

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print("SoundDevice status:", status, file=sys.stderr)
    # Vosk expects 16-bit PCM bytes. When using RawInputStream with dtype='int16', indata is bytes
    q.put(bytes(indata))

def list_devices():
    print("Available audio devices (index : name):")
    for idx, dev in enumerate(sd.query_devices()):
        print(f"{idx}: {dev['name']} (in:{dev['max_input_channels']} out:{dev['max_output_channels']})")


def find_model_path(path_hint):
    """Try to resolve a model folder. Accepts a folder name or path and
    searches nested folders for a viable Vosk model (checks for 'am' folder
    or 'model.conf' or 'final.mdl'). Returns an absolute path or None.
    """
    def looks_like_model(p):
        try:
            if not os.path.isdir(p):
                return False
            entries = set(os.listdir(p))
            # common indicators of a valid Vosk model
            indicators = {'am', 'model.conf', 'final.mdl', 'HCLr.fst'}
            return not indicators.isdisjoint(entries)
        except Exception:
            return False

    # If user passed an absolute or relative path that already looks valid, use it
    if looks_like_model(path_hint):
        return os.path.abspath(path_hint)

    # If the hint exists but is a parent folder, search one level deeper
    if os.path.isdir(path_hint):
        for name in os.listdir(path_hint):
            candidate = os.path.join(path_hint, name)
            if looks_like_model(candidate):
                return os.path.abspath(candidate)

    # Try searching current working directory for a folder that looks like a model
    cwd = os.getcwd()
    for name in os.listdir(cwd):
        candidate = os.path.join(cwd, name)
        if looks_like_model(candidate):
            return os.path.abspath(candidate)

    # As a last resort, search recursively but limit depth to avoid long scans
    for root, dirs, files in os.walk(cwd):
        # limit search depth to 3 levels from cwd
        rel = os.path.relpath(root, cwd)
        if rel.count(os.sep) > 3:
            continue
        for d in dirs:
            candidate = os.path.join(root, d)
            if looks_like_model(candidate):
                return os.path.abspath(candidate)

    return None

def validate_device(device_id, samplerate):
    """Validate if the selected audio device supports the required sample rate."""
    try:
        device_info = sd.query_devices(device_id, 'input')
        if device_info['max_input_channels'] < 1:
            raise ValueError(f"Device {device_id} does not support audio input")
        supported_samplerates = [int(sr) for sr in device_info.get('default_samplerates', [])]
        if not supported_samplerates or samplerate not in supported_samplerates:
            print(f"Warning: Device {device_id} may not support {samplerate} Hz sample rate")
        return True
    except sd.PortAudioError as e:
        raise ValueError(f"Error validating device {device_id}: {e}")

def main(model_path, device, samplerate):
    # Resolve model path (allow nested/extracted folders)
    resolved_model = find_model_path(model_path)
    if not resolved_model:
        print(f"Could not locate a Vosk model using hint '{model_path}'.\n"
              "Make sure you downloaded and extracted a model folder and pass its path via --model.\n"
              "See https://alphacephei.com/vosk/models for available models.")
        sys.exit(1)

    try:
        model = Model(resolved_model)
    except Exception:
        print(f"Failed to load Vosk model from '{resolved_model}'.\n"
              "Double-check that the folder contains model files (am/, model.conf, etc.).\n"
              "If you used a zip, ensure you extracted it and pointed to the extracted folder.")
        raise
    rec = KaldiRecognizer(model, samplerate)
    rec.SetWords(True)  # include word timing info if supported

    # Validate the audio device before proceeding
    try:
        validate_device(device, samplerate)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Opening input device index {device} at {samplerate} Hz")

    # Ensure transcripts directory exists
    transcripts_dir = os.path.join(os.getcwd(), TRANSCRIPTS_DIR)
    os.makedirs(transcripts_dir, exist_ok=True)

    # Open default transcripts file in append mode
    out_path = os.path.join(os.getcwd(), DEFAULT_OUTFILE)
    out_fh = None
    try:
        # Test if we can write to the file
        with open(out_path, "a", encoding="utf-8") as test_fh:
            test_fh.write("")
        out_fh = open(out_path, "a", encoding="utf-8")
        print(f"Appending final transcripts to: {out_path}")
    except PermissionError:
        print(f"Error: No permission to write to '{out_path}'", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: Could not open transcripts file '{out_path}': {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with sd.RawInputStream(samplerate=samplerate, blocksize=4000, dtype='int16',
                            channels=1, callback=callback, device=device) as stream:
            if not stream.active:
                raise sd.PortAudioError("Failed to start the audio stream")
            
            print("Listening... Ctrl+C to stop.")
            while True:
                try:
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        res = json.loads(rec.Result())
                        text = res.get("text", "")
                        if text:
                            print("\nFinal:", text)
                            if out_fh:
                                try:
                                    from datetime import datetime
                                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    out_fh.write(f"[{ts}] {text}\n")
                                    out_fh.flush()
                                except IOError as e:
                                    print(f"\nError writing to transcripts file: {e}", file=sys.stderr)
                    else:
                        part = json.loads(rec.PartialResult())
                        # show partial inline
                        print("Partial:", part.get("partial", ""), end="\r")
                except queue.Empty:
                    continue
    except KeyboardInterrupt:
        print("\nStopping...")
    except (sd.PortAudioError, IOError) as e:
        print(f"\nError during audio processing: {e}", file=sys.stderr)
        raise
    finally:
        if out_fh:
            try:
                out_fh.flush()
                out_fh.close()
            except IOError as e:
                print(f"Error while closing transcripts file: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vosk mic -> realtime transcription")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Path to Vosk model folder")
    parser.add_argument("--device", type=int, default=None, help="Input device index (sounddevice). If omitted, uses default input.")
    parser.add_argument("--samplerate", type=int, default=SAMPLE_RATE, help="Sample rate to use (Hz)")
    parser.add_argument("--list-devices", action="store_true", help="List sound devices and exit")
    args = parser.parse_args()

    if args.list_devices:
        list_devices()
        sys.exit(0)

    # If user didn't pass device, use default device
    device_to_use = args.device
    if device_to_use is None:
        device_to_use = sd.default.device[0]  # tuple (input, output)
        if device_to_use is None:
            print("No default input device. Use --list-devices to list available indices.", file=sys.stderr)
            sys.exit(1)
    
    try:
        main(args.model, device_to_use, args.samplerate)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)