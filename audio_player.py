import pygame
import sounddevice as sd
from pygame import mixer
import threading
import time
import queue

class AudioPlayer:
    def __init__(self):
        pygame.init()
        mixer.init()
        self.play_queue = queue.Queue()
        self.current_file = None
        self.playing_thread = None
        self.running = False

    def list_audio_devices(self):
        """List all available audio output devices"""
        print("\nQuerying audio devices...")
        try:
            devices = sd.query_devices()
            print(f"Found total {len(devices)} devices")
            output_devices = []
            
            print("\nAvailable audio output devices:")
            for i, device in enumerate(devices):
                print(f"Device {i}: {device['name']} (in:{device['max_input_channels']} out:{device['max_output_channels']})")
                if device['max_output_channels'] > 0:
                    output_devices.append(device)
            
            print(f"\nFound {len(output_devices)} output devices")
            return output_devices if output_devices else None
            
        except Exception as e:
            print(f"Error querying devices: {e}")
            return None

    def set_output_device(self, device_id):
        """Set the audio output device"""
        try:
            device_info = sd.query_devices(device_id)
            if device_info['max_output_channels'] == 0:
                raise ValueError("Selected device does not support audio output")
            
            # Configure pygame mixer for the selected device
            mixer.quit()
            mixer.init(devicename=device_info['name'])
            return True
        except Exception as e:
            print(f"Error setting output device: {e}")
            return False

    def queue_audio(self, audio_file):
        """Add an audio file to the playback queue"""
        self.play_queue.put(audio_file)

    def play_worker(self):
        """Background worker to handle audio playback"""
        while self.running:
            try:
                # Get the next audio file from the queue
                audio_file = self.play_queue.get(timeout=1)
                self.current_file = audio_file

                # Play the audio file
                mixer.music.load(audio_file)
                mixer.music.play()
                
                # Wait for the audio to finish
                while mixer.music.get_busy():
                    time.sleep(0.1)
                    if not self.running:
                        break

                self.current_file = None
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error playing audio: {e}")
                time.sleep(1)

    def start_playback_thread(self):
        """Start the background playback thread"""
        if self.playing_thread is None:
            self.running = True
            self.playing_thread = threading.Thread(target=self.play_worker, daemon=True)
            self.playing_thread.start()

    def stop_playback_thread(self):
        """Stop the background playback thread"""
        print("Stopping audio playback...")
        self.running = False
        if self.playing_thread:
            if mixer.music.get_busy():
                print("Stopping current playback...")
                mixer.music.stop()
            try:
                print("Waiting for playback thread to finish...")
                self.playing_thread.join(timeout=2)  # Wait up to 2 seconds
                if self.playing_thread.is_alive():
                    print("Warning: Audio playback thread did not stop cleanly")
            except Exception as e:
                print(f"Error stopping playback thread: {e}")
            self.playing_thread = None
        mixer.quit()  # Ensure pygame mixer is properly shut down
        print("Audio playback stopped")

    def get_current_file(self):
        """Get the currently playing audio file"""
        return self.current_file