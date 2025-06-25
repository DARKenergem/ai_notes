"""
cli.py

Command-line interface for the AI Notes App.
Supports adding, searching, listing, editing, and asking questions about notes using both semantic vector search and Gemini AI.
Includes 'ask' for Q&A over your notes, and 'ask-web' for up-to-date answers using Gemini's knowledge and the web.
"""
import typer
from rich.console import Console
from modules.db import connect_to_db
from modules.note_crud import add_note, list_notes, delete_note, edit_note
from modules.gemini_client import ask_question, ask_question_web
from modules.agent_runner import run_agents
from modules.transcription import transcribe_audio
from modules.exporter import export_notes_to_markdown, export_notes_to_html
from modules.encryption import encrypt_content, decrypt_content
import sounddevice as sd
import soundfile as sf
import tempfile
import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from modules.search_engine import add_note_to_index, remove_note_from_index, full_text_search
import numpy as np

app = typer.Typer()
console = Console()
db = connect_to_db()

@app.command()
def add(title: str, content: str = "", tags: str = "", workspace: str = "default", encrypt: bool = False, audio_path: str = ""):
    print(f"[DEBUG] CLI add called with title={title}, content={content}, tags={tags}, workspace={workspace}, encrypt={encrypt}, audio_path={audio_path}")
    tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    if encrypt and content:
        content = encrypt_content(content)
    print(f"[DEBUG] Calling add_note...")
    note_id = add_note(db, title or "", content or "", tags_list, workspace or "default", audio_path=audio_path or None)
    print(f"[DEBUG] add_note returned note_id={note_id}")
    note = db["notes"].find_one({"_id": note_id})
    if note is not None:
        run_agents(db, note)
    console.print(f"[green]Note added with ID {note_id}[/green]")

@app.command()
def add_voice(audio_path: str = "", title: str = "", tags: str = "", workspace: str = "default", encrypt: bool = False):
    try:
        print(f"[DEBUG] CLI add_voice called with audio_path={audio_path}, title={title}, tags={tags}, workspace={workspace}, encrypt={encrypt}")
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        print(f"[DEBUG] Calling add_note for voice...")
        note_id = add_note(db, title or "", "", tags_list, workspace or "default", audio_path=audio_path or None)
        print(f"[DEBUG] add_note returned note_id={note_id}")
        console.print(f"[green]Voice note added with ID {note_id}[/green]")
    except Exception as e:
        print(f"[ERROR] Exception in add_voice: {e}")
        import traceback
        traceback.print_exc()

@app.command()
def add_mic_voice(title: str = "", tags: str = "", workspace: str = "default", samplerate: int = 16000, encrypt: bool = False):
    """Record audio from the microphone and add as a voice note. User controls start/stop."""
    import threading
    import queue
    try:
        print("Press Enter to start recording...")
        input()
        print("Recording... Press Enter to stop.")
        q = queue.Queue()
        recording = True
        frames = []
        def callback(indata, frames_count, time, status):
            if status:
                print(f"[ERROR] {status}")
            q.put(indata.copy())
        stream = sd.InputStream(samplerate=samplerate, channels=1, dtype='int16', callback=callback)
        with stream:
            def stop_recording():
                nonlocal recording
                input()
                recording = False
            stopper = threading.Thread(target=stop_recording)
            stopper.start()
            while recording:
                frames.append(q.get())
            stopper.join()
        audio = np.concatenate(frames, axis=0)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            sf.write(tmpfile.name, audio, samplerate)
            tmpfile.flush()
            print(f"[green]Recording saved. Transcribing and adding note...[/green]")
            # Call add_voice directly
            add_voice(tmpfile.name, title or "", tags or "", workspace or "default", encrypt)
    except Exception as e:
        print(f"[ERROR] Exception in add_mic_voice: {e}")
        import traceback
        traceback.print_exc()

@app.command()
def list(workspace: str = "", tags: str = "", decrypt: bool = False):
    filters = {}
    if workspace:
        filters["workspace"] = workspace
    if tags:
        filters["tags"] = {"$all": [tag.strip() for tag in tags.split(",")]}
    notes = list_notes(db, filters)
    for note in notes:
        content = decrypt_content(note.get('content', '')) if decrypt and note.get('encrypted') else note.get('content', '')[:50] + ("..." if len(note.get('content', '')) > 50 else "")
        console.print(f"ID: {note.get('_id', '')} | Title: {note.get('title', '')} | Content: {content}")

@app.command()
def delete(note_id: int):
    deleted_count = delete_note(db, note_id)
    console.print(f"[red]Deleted {deleted_count} note(s)[/red]")

@app.command()
def edit(note_id: int, title: str = "", content: str = "", tags: str = "", encrypt: bool = False):
    updates = {}
    if title:
        updates["title"] = title
    if content:
        if encrypt:
            content = encrypt_content(content)
        updates["content"] = content
    if tags:
        updates["tags"] = [tag.strip() for tag in tags.split(",")]
    modified_count = edit_note(db, note_id, updates)
    if modified_count:
        note = db["notes"].find_one({"_id": note_id})
        if note is not None:
            run_agents(db, note)
    console.print(f"[yellow]Modified {modified_count} note(s)[/yellow]")

@app.command()
def ask(question: str):
    """
    Ask a question about your notes using Gemini AI (Q&A over your own notes).
    Uses semantic vector search to find relevant notes and provides them as context to Gemini.
    """
    answer = ask_question(db, question)
    console.print(f"[blue]Answer:[/blue] {answer}")

@app.command()
def ask_web(question: str):
    """
    Ask a question and get an up-to-date answer from Gemini AI (web-powered).
    Gemini will use its latest knowledge and may incorporate your notes as context if relevant.
    Use this for questions about current events, news, or anything requiring the latest information.
    """
    answer = ask_question_web(db, question)
    console.print(f"[blue]Answer:[/blue] {answer}")

@app.command()
def export(workspace: str = "", tags: str = "", format: str = "markdown", output: str = ""):
    filters = {}
    if workspace:
        filters["workspace"] = workspace
    if tags:
        filters["tags"] = {"$all": [tag.strip() for tag in tags.split(",")]}
    notes = list_notes(db, filters)
    if format == "markdown":
        content = export_notes_to_markdown(notes, output or None)
    elif format == "html":
        content = export_notes_to_html(notes, output or None)
    console.print(f"[green]Exported to {output or 'console'}[/green]")

@app.command()
def init_db():
    """Initialize MongoDB collections with schema validation from schema JSON files."""
    load_dotenv("api.env")
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
    with open("notes.schema.json") as f:
        notes_schema = json.load(f)
    with open("counters.schema.json") as f:
        counters_schema = json.load(f)
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    # Create 'notes' collection with schema validation
    try:
        db.create_collection(
            "notes",
            validator={"$jsonSchema": notes_schema},
            validationLevel="strict"
        )
        console.print("[green]'notes' collection created with schema validation.[/green]")
    except Exception as e:
        if "already exists" in str(e):
            console.print("[yellow]'notes' collection already exists.[/yellow]")
        else:
            console.print(f"[red]Error creating 'notes' collection: {e}[/red]")
    # Create 'counters' collection with schema validation
    try:
        db.create_collection(
            "counters",
            validator={"$jsonSchema": counters_schema},
            validationLevel="strict"
        )
        console.print("[green]'counters' collection created with schema validation.[/green]")
    except Exception as e:
        if "already exists" in str(e):
            console.print("[yellow]'counters' collection already exists.[/yellow]")
        else:
            console.print(f"[red]Error creating 'counters' collection: {e}[/red]")

@app.command()
def search(query: str):
    """Full-text search notes by title and content."""
    results = full_text_search(db, query)
    if not results:
        console.print(f"[yellow]No results found for: {query}[/yellow]")
    for note in results:
        content = note.get('content', '')[:50] + ("..." if len(note.get('content', '')) > 50 else "")
        console.print(f"ID: {note.get('_id', '')} | Title: {note.get('title', '')} | Content: {content}")

if __name__ == "__main__":
    app()