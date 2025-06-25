from datetime import datetime
from modules.db import get_next_note_id
from modules.search_engine import add_note_to_index, remove_note_from_index
from modules.audio_to_text import transcribe_audio

def add_note(db, title, content=None, tags=None, workspace=None, audio_path=None):
    """
    Add a note to the database. If audio_path is provided, transcribe the audio and use the result as content.
    """
    print(f"[DEBUG] add_note called with title={title}, tags={tags}, workspace={workspace}, audio_path={audio_path}")
    if audio_path:
        print(f"[DEBUG] Transcribing audio for note: {audio_path}")
        content = transcribe_audio(audio_path)
    # fallback for tags and workspace
    if tags is None:
        tags = []
    if workspace is None:
        workspace = "default"
    note_id = get_next_note_id(db)
    print(f"[DEBUG] Inserting note with note_id={note_id}")
    note = {
        "_id": note_id,
        "title": title,
        "content": content,
        "tags": tags,
        "workspace": workspace,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    db["notes"].insert_one(note)
    add_note_to_index(note_id, content)
    print(f"[DEBUG] Note inserted and indexed: {note_id}")
    return note_id

def list_notes(db, filters):
    return list(db["notes"].find(filters))

def delete_note(db, note_id):
    result = db["notes"].delete_one({"_id": note_id})
    if result.deleted_count:
        remove_note_from_index(note_id)
    return result.deleted_count

def edit_note(db, note_id, updates):
    if "content" in updates:
        remove_note_from_index(note_id)
    result = db["notes"].update_one({"_id": note_id}, {"$set": updates})
    if "content" in updates and result.modified_count:
        add_note_to_index(note_id, updates["content"])
    return result.modified_count