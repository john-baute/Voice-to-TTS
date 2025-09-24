import sounddevice as sd
import numpy as np
import queue
from faster_whisper import WhisperModel
from TTS.api import TTS

# ========================
# Settings
# ========================
SAMPLE_RATE = 16000
BLOCK_SIZE = 1024
SILENCE_THRESHOLD = 0.01   # mic sensitivity
SILENCE_DURATION = 1.5     # seconds of silence = end of phrase
OUTPUT_DEVICE = None       # change to VB-Cable / BlackHole later

# ========================
# Load Models
# ========================
print("Loading models...")
stt_model = WhisperModel("base.en")  # lightweight English STT
tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")  # TTS voice
print("✅ Models loaded")

# ========================
# Audio Queue
# ========================
q_in = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print("⚠️", status)
    q_in.put(indata.copy())

# ========================
# Main Loop
# ========================
def main():
    print("🎤 Speak... (pause for transcription)")
    with sd.InputStream(samplerate=SAMPLE_RATE,
                        channels=1,
                        blocksize=BLOCK_SIZE,
                        callback=callback):

        buffer = np.zeros(0, dtype=np.float32)
        silence_time = 0
        speaking = False

        while True:
            chunk = q_in.get().flatten()
            buffer = np.concatenate((buffer, chunk))

            # Volume = RMS energy
            volume = np.sqrt(np.mean(chunk**2))

            if volume > SILENCE_THRESHOLD:
                speaking = True
                silence_time = 0
            else:
                if speaking:
                    silence_time += BLOCK_SIZE / SAMPLE_RATE
                    if silence_time >= SILENCE_DURATION:
                        # End of phrase detected
                        print("🔎 Transcribing...")
                        segments, _ = stt_model.transcribe(buffer, beam_size=1)
                        text = " ".join([seg.text for seg in segments]).strip()
                        print("📝 You said:", text)

                        if text:
                            wav = tts_model.tts(text)
                            sd.play(wav, samplerate=22050, device=OUTPUT_DEVICE)
                            sd.wait()

                        # Reset buffer
                        buffer = np.zeros(0, dtype=np.float32)
                        silence_time = 0
                        speaking = False

if __name__ == "__main__":
    main()