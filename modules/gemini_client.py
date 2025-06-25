"""
gemini_client.py

Handles integration with Gemini AI for Q&A, rephrasing, and up-to-date answers.
- ask_question: Q&A over your notes (context from semantic vector search)
- ask_question_web: Up-to-date answers using Gemini's latest knowledge and optionally your notes
"""
import google.generativeai as gemini
import os
from dotenv import load_dotenv
from modules.search_engine import search_similar_notes, full_text_search
from typing import List

# Load environment variables from api.env file
load_dotenv("api.env")

_gemini_configured = False
_qa_cache = {}

def _ensure_gemini():
    """
    Ensure Gemini API is configured with the API key from environment variables.
    """
    global _gemini_configured
    print("[DEBUG] Ensuring Gemini API is configured...")
    if not _gemini_configured:
        key = os.getenv("GEMINI_API_KEY", "default_key")
        if not key:
            print("[ERROR] GEMINI_API_KEY not set!")
            raise EnvironmentError("GEMINI_API_KEY not set")
        gemini.configure(api_key=key)
        _gemini_configured = True
        print("[DEBUG] Gemini API configured.")
    else:
        print("[DEBUG] Gemini API already configured.")

def generate_response(prompt, use_web_search=False):
    """
    Generate a response from Gemini AI.
    If use_web_search is True, prompt Gemini to provide up-to-date information (best effort).
    """
    print(f"[DEBUG] Generating Gemini response for prompt: {prompt}")
    _ensure_gemini()
    try:
        if use_web_search:
            # Use Gemini 1.5 Pro with web search enabled (best effort via prompt)
            model = gemini.GenerativeModel('gemini-1.5-pro')
            web_prompt = f"Please search the web for current information and answer: {prompt}"
            response = model.generate_content(web_prompt)
        else:
            model = gemini.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
        print(f"[DEBUG] Gemini response: {response.text}")
        return response.text
    except Exception as e:
        print(f"[Gemini ERROR] Failed to generate response for prompt: {prompt}\nError: {e}")
        return "[AI response failed]"

def ask_question(db, question, k=5):
    """
    Ask Gemini a question about your notes.
    Uses semantic vector search (FAISS) and full-text search to find relevant notes, then provides them as context to Gemini.
    """
    print(f"[DEBUG] ask_question called with question: {question}, k={k}")
    if question in _qa_cache:
        print("[DEBUG] Returning cached answer.")
        return _qa_cache[question]
    
    # Search for relevant notes using semantic search
    print("[DEBUG] Searching for relevant notes...")
    similar_note_ids = search_similar_notes(question, k)
    
    # Also do full-text search for additional context
    full_text_results = full_text_search(db, question)
    
    # Get the actual note content
    relevant_notes = []
    
    # Get notes from semantic search
    if similar_note_ids:
        semantic_notes = list(db["notes"].find({"_id": {"$in": similar_note_ids}}))
        relevant_notes.extend(semantic_notes)
    
    # Get notes from full-text search (avoid duplicates)
    full_text_ids = [note["_id"] for note in full_text_results]
    for note in full_text_results:
        if note["_id"] not in similar_note_ids:
            relevant_notes.append(note)
    
    if not relevant_notes:
        print("[DEBUG] No relevant notes found.")
        response = "I couldn't find any notes that match your question. Please try adding some notes first or rephrase your question."
        _qa_cache[question] = response
        return response
    
    # Prepare context from relevant notes
    context = "Based on the following notes:\n\n"
    for i, note in enumerate(relevant_notes[:k], 1):
        title = note.get("title", "Untitled")
        content = note.get("content", "")
        tags = ", ".join(note.get("tags", []))
        workspace = note.get("workspace", "default")
        
        context += f"Note {i}:\n"
        context += f"Title: {title}\n"
        context += f"Content: {content}\n"
        context += f"Tags: {tags}\n"
        context += f"Workspace: {workspace}\n"
        context += f"Date: {note.get('created_at', 'Unknown')}\n"
        context += "-" * 50 + "\n\n"
    
    # Create the prompt with context
    prompt = f"{context}\n\nQuestion: {question}\n\nPlease answer the question based on the notes provided above. If the notes don't contain enough information to answer the question, please say so."
    
    response = generate_response(prompt)
    _qa_cache[question] = response
    print(f"[DEBUG] ask_question response: {response}")
    return response

def ask_question_web(db, question, k=5):
    """
    Ask Gemini for an up-to-date answer, using its latest knowledge and optionally your notes as context.
    Use this for questions about current events, news, or anything requiring the latest information.
    """
    print(f"[DEBUG] ask_question_web called with question: {question}, k={k}")
    
    # Search for relevant notes (optional, for extra context)
    similar_note_ids = search_similar_notes(question, k)
    full_text_results = full_text_search(db, question)
    relevant_notes = []
    if similar_note_ids:
        semantic_notes = list(db["notes"].find({"_id": {"$in": similar_note_ids}}))
        relevant_notes.extend(semantic_notes)
    for note in full_text_results:
        if note["_id"] not in similar_note_ids:
            relevant_notes.append(note)
    
    # Prepare notes context if available
    notes_context = ""
    if relevant_notes:
        notes_context = "\n\nAlso consider these relevant notes from your database:\n\n"
        for i, note in enumerate(relevant_notes[:k], 1):
            title = note.get("title", "Untitled")
            content = note.get("content", "")
            tags = ", ".join(note.get("tags", []))
            workspace = note.get("workspace", "default")
            notes_context += f"Note {i}:\nTitle: {title}\nContent: {content}\nTags: {tags}\nWorkspace: {workspace}\nDate: {note.get('created_at', 'Unknown')}\n{'-'*50}\n\n"
    
    # Create the prompt for comprehensive answer
    prompt = f"Please provide a comprehensive and up-to-date answer to this question: {question}{notes_context}\n\nPlease provide current information and insights. If there are relevant notes from the user's database, incorporate that context as well. If the question requires very recent information that might not be in your training data, please note that and provide the best available information."
    
    # Use Gemini with the enhanced prompt
    response = generate_response(prompt, use_web_search=False)  # Use regular model for now
    print(f"[DEBUG] ask_question_web response: {response}")
    return response