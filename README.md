# 📝 AI Notes App

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![MongoDB](https://img.shields.io/badge/database-mongodb-green)
![CLI](https://img.shields.io/badge/interface-cli-orange)
![AI](https://img.shields.io/badge/AI-Gemini%20%26%20Embeddings-purple)

A modern, AI-powered note-taking app with:
- ✍️ **Text & Voice Notes** (voice-to-text transcription, interactive mic recording)
- 🔍 **Semantic & Full-Text Search** (FAISS vector search + MongoDB)
- 🤖 **Gemini AI Integration** (rephrase, Q&A, tag suggestions, up-to-date answers)
- 🌐 **Ask the Web** (ask-web command for up-to-date answers using Gemini)
- 📤 **Export to Markdown & HTML**
- 🖥️ **Rich CLI Experience** (Typer + Rich)
- 🔐 **Encryption** for sensitive notes
- 📅 **Calendar & WhatsApp Automation**

---

## 🚀 Features
- **Add notes** via text, audio file, or live microphone (interactive start/stop)
- **Semantic search** using embeddings (FAISS vector database)
- **Full-text search** with MongoDB
- **AI-powered actions**: rephrase, tag, Q&A (Gemini)
- **Ask the Web**: Get up-to-date answers from Gemini with the `ask-web` command
- **Export** notes to Markdown/HTML
- **Calendar & WhatsApp integration** (ICS, share logs)
- **Encryption** for sensitive notes
- **Automated agents** for smart triggers

### 🔐 Security
- **Content Encryption**: Encrypt sensitive notes using Fernet encryption
- **Environment-based Keys**: Secure key management

### 🤖 Automated Agents
- **Calendar Integration**: Automatically create calendar events for tagged notes
- **WhatsApp Sharing**: Share notes via WhatsApp (with file generation)
- **Smart Triggers**: Rule-based automation based on note tags

### 📊 Export & Organization
- **Multiple Formats**: Export to Markdown and HTML
- **Workspace Support**: Organize notes by workspaces
- **Rich CLI**: Beautiful command-line interface with Typer

## 🛠️ Installation

1. **Clone the repository**
   ```sh
   git clone <repository-url>
   cd project-notes
   ```
2. **Create & activate a virtual environment**
   ```sh
   python -m venv noteses
   ./noteses/Scripts/activate  # Windows
   source noteses/bin/activate  # Linux/Mac
   ```
3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Set up environment variables**
   - Copy `api.env.example` to `api.env` and fill in your MongoDB and Gemini API keys.

---

## 📦 Requirements

- **faiss-cpu**: Fast vector search for semantic similarity
- **numpy**: Numerical operations
- **sentence-transformers**: Text embeddings (384-dim vectors)
- **python-dotenv**: Environment variable management
- **pymongo**: MongoDB client
- **typer**: CLI framework
- **rich**: Beautiful CLI output
- **sounddevice, soundfile**: Audio recording and file handling
- **SpeechRecognition**: Speech-to-text
- **google-generativeai**: Gemini AI integration (Q&A, rephrase, up-to-date answers)
- **jinja2**: Export templates
- **cryptography**: Note encryption
- **pytest, mongomock**: Testing

---

## 💡 Usage

### Add a text note
```sh
python -m modules.cli add "Meeting Notes" --content "Discussed project roadmap." --tags "meeting,project"
```

### Add a voice note from an audio file
```sh
python -m modules.cli add_voice --audio-path path/to/audio.wav --title "Voice Note" --tags "voice,meeting"
```

### Add a voice note from your microphone (interactive)
```sh
python -m modules.cli add-mic-voice --title "Mic Note" --tags "mic,live" --workspace "default"
# Press Enter to start, speak, then Enter again to stop
```

### List notes
```sh
python -m modules.cli list --tags meeting
```

### Search notes
```sh
python -m modules.cli search "roadmap"
```

### Ask a question about your notes (Gemini Q&A)
```sh
python -m modules.cli ask "What did I discuss in the last meeting?"
```

### Ask the web (up-to-date Gemini answer)
```sh
python -m modules.cli ask-web "Tell me about the latest global events"
```

### Export notes
```sh
python -m modules.cli export --format markdown --output notes.md
```

### CLI Commands & Functionality

| Command         | Description                                                                                       | Example Usage                                                                                       |
|-----------------|---------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| add             | Add a new note with title, content, tags, workspace, encryption, or audio file.                   | python -m modules.cli add "Title" --content "Text" --tags "tag1,tag2" --workspace "default"         |
| add-voice       | Add a voice note from an audio file.                                                              | python -m modules.cli add-voice --audio-path path/to/audio.wav --title "Voice Note" --tags "voice"   |
| add-mic-voice   | Record audio from the microphone and add as a voice note (interactive start/stop).                | python -m modules.cli add-mic-voice --title "Mic Note" --tags "mic,live" --workspace "default"      |
| list            | List notes, optionally filtered by workspace or tags. Optionally decrypt content.                  | python -m modules.cli list --tags meeting --decrypt                                                 |
| delete          | Delete a note by its ID.                                                                          | python -m modules.cli delete 123                                                                     |
| edit            | Edit a note's title, content, tags, or encryption by ID.                                          | python -m modules.cli edit 123 --title "New Title" --content "Updated" --tags "tag1,tag2"           |
| ask             | Ask a question about your notes (Gemini AI Q&A).                                                  | python -m modules.cli ask "What did I discuss in the last meeting?"                                 |
| ask-web         | Ask a question and get an up-to-date answer from Gemini (web-powered, may use your notes too).     | python -m modules.cli ask-web "Tell me about the latest global events"                              |
| export          | Export notes to Markdown or HTML, filtered by workspace/tags, to a file or console.               | python -m modules.cli export --format markdown --output notes.md                                     |
| init-db         | Initialize MongoDB collections with schema validation (requires schema files).                     | python -m modules.cli init-db                                                                        |
| search          | Full-text search notes by title and content.                                                      | python -m modules.cli search "roadmap"                                                              |

---

## 🤖 AI & Automation
- **Rephrase notes**: Gemini AI can rephrase your notes for clarity.
- **Suggest tags**: Get smart tag suggestions.
- **Q&A**: Ask questions about your notes.
- **Ask the Web**: Get up-to-date answers from Gemini with `ask-web`.
- **Automated agents**: Calendar events, WhatsApp sharing, and more based on tags.

---

## 🗂️ Project Structure
```
project-notes/
  modules/
    cli.py           # CLI entry point
    note_crud.py     # Note CRUD logic
    search_engine.py # Semantic & full-text search (FAISS vectors)
    gemini_client.py # Gemini AI integration (Q&A, ask-web)
    audio_to_text.py # Voice-to-text
    ...
  tests/             # Test files
  requirements.txt   # Dependencies
  README.md          # This file
```

---

## 🛠️ Troubleshooting
- **No audio recorded?** Check your microphone permissions and device.
- **Transcription failed?** Ensure you speak clearly and have an internet connection for Google Speech API.
- **No notes listed?** Make sure MongoDB is running and your environment variables are set.
- **ffmpeg required** for some audio conversions (install from https://ffmpeg.org/ if needed).
- **Gemini API quota exceeded?** If you see errors like `429 You exceeded your current quota`, wait for your quota to reset or upgrade your Gemini API plan. See [Gemini API Quotas](https://ai.google.dev/gemini-api/docs/rate-limits).

---

## 🧑‍💻 Contributing
Pull requests welcome! Please open an issue first to discuss major changes.

---

## 📄 License
MIT