import gtts
import os
import threading
from audio_player import AudioPlayer
from file_manager import FileManager

# Global instances
audio_player = None
file_manager = None

def initialize(device_id=None, retention_minutes=1):
    """Initialize the audio player and file manager"""
    global audio_player, file_manager
    
    # Initialize audio player
    audio_player = AudioPlayer()
    if device_id is not None:
        audio_player.set_output_device(device_id)
    audio_player.start_playback_thread()
    
    # Initialize file manager
    file_manager = FileManager(retention_minutes=retention_minutes)
    file_manager.start_cleanup_thread()

def list_audio_devices():
    """List available audio output devices"""
    global audio_player
    print("Initializing audio player...")  # Debug line
    if not audio_player:
        audio_player = AudioPlayer()
    print("Calling list_audio_devices...")  # Debug line
    devices = audio_player.list_audio_devices()
    print(f"Found {len(devices) if devices else 0} output devices")  # Debug line
    return devices

def text_to_speech(text, lang='en', output_file='audio_clips/output.mp3'):
    """Convert text to speech, save as an mp3 file, and queue for playback."""
    global audio_player, file_manager
    
    # Ensure the audio_clips directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Generate the speech
    tts = gtts.gTTS(text, lang=lang)
    tts.save(output_file)
    print(f"Saved TTS output to {output_file}")
    
    # Mark the file as active (with 5 minute duration) and queue it for playback
    if file_manager:
        file_manager.mark_file_active(output_file, duration_minutes=1)
    
    if audio_player:
        audio_player.queue_audio(output_file)

def cleanup():
    """Clean up resources"""
    global audio_player, file_manager
    
    print("Starting cleanup...")
    
    # Stop audio player
    if audio_player:
        print("Stopping audio player...")
        audio_player.stop_playback_thread()
        
    # Stop file manager
    if file_manager:
        print("Stopping file manager...")
        file_manager.stop_cleanup_thread()
        
    print("Cleanup completed")