import os
import time
from datetime import datetime, timedelta
import threading

class FileManager:
    def __init__(self, retention_minutes=1):
        self.retention_period = timedelta(minutes=retention_minutes)
        self.cleanup_thread = None
        self.running = False
        self.active_files = {}  # Changed to dict to store expiration times
        
        # Ensure required directories exist
        os.makedirs("audio_clips", exist_ok=True)
        os.makedirs("transcripts", exist_ok=True)

    def mark_file_active(self, filepath, duration_minutes=1):
        """Mark a file as currently in use"""
        filepath = os.path.abspath(filepath)
        expiration_time = datetime.now() + timedelta(minutes=duration_minutes)
        self.active_files[filepath] = expiration_time
        print(f"File {filepath} marked active until {expiration_time}")

    def is_file_active(self, filepath):
        """Check if a file is still active"""
        filepath = os.path.abspath(filepath)
        if filepath not in self.active_files:
            return False
        
        now = datetime.now()
        expiration_time = self.active_files[filepath]
        
        if now > expiration_time:
            del self.active_files[filepath]
            return False
            
        return True

    def cleanup_files(self, directory):
        """Remove old files from the specified directory"""
        # Ensure directory exists
        os.makedirs(directory, exist_ok=True)
        
        now = datetime.now()
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if self.is_file_active(filepath):
                continue
                
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                age = now - mtime
                
                if age > self.retention_period:
                    os.remove(filepath)
                    print(f"Removed stale file: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    def cleanup_worker(self):
        """Background worker to periodically clean up files"""
        while self.running:
            try:
                # Clean up both transcripts and audio clips directories
                self.cleanup_files("transcripts")
                self.cleanup_files("audio_clips")
            except Exception as e:
                print(f"Error during cleanup: {e}")
            
            # Sleep for 1 hour before next cleanup
            time.sleep(3600)

    def start_cleanup_thread(self):
        """Start the background cleanup thread"""
        if self.cleanup_thread is None:
            print("Starting file cleanup thread...")
            self.running = True
            self.cleanup_thread = threading.Thread(target=self.cleanup_worker, daemon=True)
            self.cleanup_thread.start()

    def stop_cleanup_thread(self):
        """Stop the background cleanup thread"""
        print("Stopping file cleanup thread...")
        self.running = False
        if self.cleanup_thread:
            try:
                print("Waiting for cleanup thread to finish...")
                self.cleanup_thread.join(timeout=2)  # Wait up to 2 seconds
                if self.cleanup_thread.is_alive():
                    print("Warning: Cleanup thread did not stop cleanly")
            except Exception as e:
                print(f"Error stopping cleanup thread: {e}")
            self.cleanup_thread = None
        print("File cleanup stopped")