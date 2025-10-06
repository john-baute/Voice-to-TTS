import sounddevice as sd

def test_audio_devices():
    devices = sd.query_devices()
    print("\nAll audio devices:")
    for i, device in enumerate(devices):
        print(f"{i}: {device['name']} (in:{device['max_input_channels']} out:{device['max_output_channels']})")

if __name__ == "__main__":
    test_audio_devices()