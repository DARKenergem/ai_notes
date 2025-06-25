"""
search_engine.py

Provides semantic vector search for notes using FAISS and sentence-transformers.
All semantic search is performed using 384-dimensional embeddings (vectors) for fast similarity search.
"""
import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables from api.env file
load_dotenv("api.env")

_model = None
_index = None
_index_modified = False
EMBEDDING_DIM = 384
INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "index.faiss")

def get_model():
    """
    Load or return the cached sentence-transformer model for generating text embeddings (vectors).
    """
    global _model
    if _model is None:
        print("[DEBUG] Loading SentenceTransformer model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    else:
        print("[DEBUG] Using cached SentenceTransformer model.")
    return _model

def load_index():
    """
    Load or create the FAISS vector index for semantic search.
    """
    global _index, _index_modified
    if _index is None:
        if os.path.exists(INDEX_PATH):
            print(f"[DEBUG] Loading FAISS index from {INDEX_PATH}")
            _index = faiss.read_index(INDEX_PATH)
        else:
            print(f"[DEBUG] Creating new FAISS index at {INDEX_PATH}")
            _index = faiss.IndexIDMap2(faiss.IndexFlatL2(EMBEDDING_DIM))
        _index_modified = False
    else:
        print("[DEBUG] Using cached FAISS index.")
    return _index

def save_index():
    """
    Save the FAISS index to disk if it has been modified.
    """
    global _index, _index_modified
    if _index is not None and _index_modified:
        print(f"[DEBUG] Saving FAISS index to {INDEX_PATH}")
        faiss.write_index(_index, INDEX_PATH)
        _index_modified = False
    else:
        print("[DEBUG] No changes to FAISS index; skipping save.")

def add_note_to_index(note_id, content):
    """
    Add a note's content as a vector to the FAISS index for semantic search.
    """
    print(f"[DEBUG] Adding note to index: note_id={note_id}")
    idx = load_index()
    embedding = get_model().encode(content)
    idx.add_with_ids(np.array([embedding], dtype=np.float32), np.array([note_id], dtype=np.int64))
    global _index_modified
    _index_modified = True
    print(f"[DEBUG] Note {note_id} added to FAISS index.")

def remove_note_from_index(note_id):
    """
    Remove a note's vector from the FAISS index.
    """
    print(f"[DEBUG] Removing note from index: note_id={note_id}")
    idx = load_index()
    idx.remove_ids(np.array([note_id], dtype=np.int64))
    global _index_modified
    _index_modified = True
    print(f"[DEBUG] Note {note_id} removed from FAISS index.")

def search_similar_notes(query, k=5):
    """
    Perform semantic vector search for notes most similar to the query string.
    Returns a list of note IDs ranked by vector similarity.
    """
    print(f"[DEBUG] Searching for notes similar to: '{query}' (top {k})")
    idx = load_index()
    model = get_model()
    query_embedding = model.encode(query)
    distances, indices = idx.search(np.array([query_embedding], dtype=np.float32), k)
    print(f"[DEBUG] Search results: indices={indices}, distances={distances}")
    return [int(i) for i in indices[0] if i != -1]

def ensure_text_index(db):
    """
    Ensure a MongoDB text index exists for full-text search on title and content fields.
    """
    print("[DEBUG] Ensuring text index exists on 'notes' collection.")
    # Ensure a text index exists on 'title' and 'content'
    if 'notes' in db.list_collection_names():
        indexes = db['notes'].index_information()
        for idx in indexes.values():
            if 'key' in idx and any(isinstance(k, tuple) and k[1] == 'text' for k in idx['key']):
                print("[DEBUG] Text index already exists.")
                return  # Text index exists
        db['notes'].create_index([('title', 'text'), ('content', 'text')])
        print("[DEBUG] Text index created.")
    else:
        print("[DEBUG] 'notes' collection does not exist.")

def full_text_search(db, query):
    """
    Perform full-text search for notes using MongoDB's text index.
    Returns a list of matching notes.
    """
    print(f"[DEBUG] Performing full-text search for: '{query}'")
    ensure_text_index(db)
    results = list(db['notes'].find({'$text': {'$search': query}}))
    print(f"[DEBUG] Full-text search found {len(results)} results.")
    return results