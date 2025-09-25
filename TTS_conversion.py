import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
import tempfile
import os

def list_devices_verbose():
    hostapis = sd.query_hostapis()
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        hostapi_name = hostapis[d['hostapi']]['name'] if d['hostapi'] < len(hostapis) else str(d['hostapi'])
        print(f"{i}: {d['name']} | hostapi: {hostapi_name} | in:{d['max_input_channels']} out:{d['max_output_channels']} sr:{int(d['default_samplerate'])}")

def find_output_devices_by_name_substring(sub):
    matches = []
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()
    for i, d in enumerate(devices):
        if sub.lower() in d['name'].lower() and d['max_output_channels'] > 0 and d['hostapi'] == 'WASAPI':
            matches.append((i, d))
    return matches

def get_device_index_by_name(name):
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if d['name'] == name:
            return i, d
    raise RuntimeError(f"Device named '{name}' not found")

def play_file_to_device(path, device_index):
    data, sr = sf.read(path, dtype='float32')
    sd.play(data, sr, device=device_index)
    sd.wait()

def play_mp3_to_device(mp3_path, device_index):
    audio = AudioSegment.from_file(mp3_path)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        wav_path = tmp.name
    audio.export(wav_path, format="wav")
    try:
        play_file_to_device(wav_path, device_index)
    finally:
        os.remove(wav_path)

if __name__ == "__main__":
    print("Available audio devices (index : name | hostapi | in/out | samplerate):")
    list_devices_verbose()

    # Hardcode by exact device name (safer than index). Replace with your device name if different.
    target_name = "CABLE Output (VB-Audio Virtual Cable)"
    try:
        device_idx, device_info = get_device_index_by_name(target_name)
        print(f"\nFound device '{target_name}' at index {device_idx} (in:{device_info['max_input_channels']} out:{device_info['max_output_channels']})")
        if device_info['max_output_channels'] == 0:
            print("Warning: this device is input-only (it's a virtual microphone). You cannot play audio to it.")
            print("To send audio into the virtual cable, play to the corresponding 'CABLE Input (VB-Audio Virtual Cable)' device (the one with out>0).")
        else:
            print("Using this device for playback.")
            # Replace with your generated TTS file
            play_mp3_to_device("tts_output.mp3", device_idx)
    except RuntimeError as e:
        print(e)
        print("Falling back to interactive selection or substring search.")