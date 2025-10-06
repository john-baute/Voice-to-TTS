from transcript_to_tts import text_to_speech, initialize, list_audio_devices, cleanup
from transcription import main as transcribe_audio
import os
import sys
from datetime import datetime
import atexit

def process_transcription(text):
    """Handle completed transcription by converting it to speech"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'audio_clips/transcript_{timestamp}.mp3'
    os.makedirs('audio_clips', exist_ok=True)
    text_to_speech(text, output_file=output_file)

def setup_audio_output():
    """Set up the audio output device"""
    print("\nSetting up audio output...")  # Debug line
    devices = list_audio_devices()
    
    if not devices:
        print("No audio output devices found!")
        sys.exit(1)
    
    print("\nPlease select an output device:")
    device_id = input("Enter device number (or press Enter for default): ").strip()
    
    if device_id:
        try:
            device_id = int(device_id)
            print(f"Selected device ID: {device_id}")  # Debug line
        except ValueError:
            print("Invalid device number, using default")
            device_id = None
    else:
        print("Using default device")  # Debug line
        device_id = None
    
    return device_id

if __name__ == "__main__":
    try:
        # Set up audio output
        device_id = setup_audio_output()
        
        # Initialize audio and file management systems
        initialize(device_id=device_id, retention_minutes=1)
        
        # Register cleanup function for normal program exit
        atexit.register(cleanup)
        
        # Start transcription
        try:
            transcribe_audio(callback_fn=process_transcription)
        except KeyboardInterrupt:
            print("\nReceived keyboard interrupt, shutting down...")
        
    except Exception as e:
        print(f"\nError during execution: {e}")
    finally:
        # Ensure cleanup runs even if there's an error during setup
        try:
            cleanup()
            atexit.unregister(cleanup)  # Prevent duplicate cleanup
        except Exception as e:
            print(f"Error during cleanup: {e}")