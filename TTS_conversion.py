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
    for i, d in enumerate(devices):
        if sub.lower() in d['name'].lower() and d['max_output_channels'] > 0:
            matches.append((i, d))
    return matches

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

    # Try common substrings; adjust if your devices use different names
    # substrings = ["cable", "(vb-audio", "voice", "voicemeeter"]
    # matches = []
    # for s in substrings:
    #     matches = find_output_devices_by_name_substring(s)
    #     if matches:
    #         print(f"\nFound devices matching '{s}':")
    #         break

    # if not matches:
    #     # fallback: list all output-capable devices
    #     devices = sd.query_devices()
    #     matches = [(i, d) for i, d in enumerate(devices) if d['max_output_channels'] > 0]
    #     print("\nNo specific 'Cable' devices found — showing all output-capable devices:")

    # for i, d in matches:
    #     print(f"{i}: {d['name']} | out:{d['max_output_channels']} sr:{int(d['default_samplerate'])}")

    # if len(matches) == 1:
    #     device_idx = matches[0][0]
    #     print(f"\nAuto-selecting device index {device_idx}")
    # else:
    #     # ask user to pick the index from the printed list
    #     while True:
    #         try:
    #             choice = input("\nEnter the device index to use (or press Enter to use the first match): ").strip()
    #             if choice == "":
    #                 device_idx = matches[0][0]
    #                 break
    #             device_idx = int(choice)
    #             # validate
    #             if any(device_idx == m[0] for m in matches):
    #                 break
    #             print("Index not in the listed matches. Try again.")
    #         except ValueError:
    #             print("Please enter a valid integer index.")

    # print("Using device index", device_idx)
    # # Replace with your generated TTS file
    # play_mp3_to_device("tts_output.mp3", device_idx)