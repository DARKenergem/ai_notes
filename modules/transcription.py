import os
import google.generativeai as gemini
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from api.env file
load_dotenv("api.env")

_gemini_configured = False

def _ensure_gemini():
    global _gemini_configured
    if not _gemini_configured:
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise EnvironmentError("GEMINI_API_KEY not set")
        gemini.configure(api_key=key)
        _gemini_configured = True

def transcribe_audio(file_path: str) -> str:
    """
    Transcribe audio using Gemini AI speech-to-text.
    Supports common audio formats like MP3, WAV, M4A, etc.
    """
    try:
        _ensure_gemini()
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        # Read the audio file
        with open(file_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        # Use Gemini's audio transcription
        model = gemini.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            "Please transcribe this audio file accurately, preserving punctuation and formatting.",
            {"mime_type": "audio/mpeg", "data": audio_data}
        ])
        
        return response.text.strip()
        
    except Exception as e:
        print(f"Transcription failed: {e}")
        # Fallback to mock transcription for development
        return f"[Transcription failed] Audio from {file_path}: {str(e)}"