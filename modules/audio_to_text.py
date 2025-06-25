import speech_recognition as sr


def transcribe_audio(audio_path):
    """
    Transcribe an audio file to text using Google Web Speech API (via SpeechRecognition).
    Supports common audio formats (wav, m4a, mp3, etc.).
    Returns the transcribed text as a string, or raises an exception on failure.
    """
    recognizer = sr.Recognizer()
    print(f"[DEBUG] Starting transcription for: {audio_path}")
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        print(f"[DEBUG] Audio loaded, sending to Google Web Speech API...")
        text = recognizer.recognize_google(audio)
        print(f"[DEBUG] Transcription result: {text}")
        return text
    except Exception as e:
        print(f"[ERROR] Transcription failed for {audio_path}: {e}")
        raise RuntimeError(f"Transcription failed: {e}") 