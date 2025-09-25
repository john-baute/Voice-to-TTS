import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
import tempfile
import os

def list_devices():
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        # d is a dict with keys including 'name'
        print(i, d['name'])

def find_device_index_by_name_substring(sub):
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if sub.lower() in d['name'].lower():
            return i
    raise RuntimeError(f"Device containing '{sub}' not found")

def play_file_to_device(path, device_index):
    data, sr = sf.read(path, dtype='float32')
    sd.play(data, sr, device=device_index)
    sd.wait()

def play_mp3_to_device(mp3_path, device_index):
    # Convert mp3 to wav in memory (temporary file) using pydub
    audio = AudioSegment.from_file(mp3_path)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        wav_path = tmp.name
    audio.export(wav_path, format="wav")
    try:
        play_file_to_device(wav_path, device_index)
    finally:
        os.remove(wav_path)

if __name__ == "__main__":
    print("Available audio devices:")
    list_devices()
    # Change the substring to match your device name; typical: "cable" or "vb-audio"
    # device_idx = find_device_index_by_name_substring("cable")
    # print("Using device index", device_idx)
    # # Replace with your generated TTS file
    # play_mp3_to_device("tts_output.mp3", device_idx)