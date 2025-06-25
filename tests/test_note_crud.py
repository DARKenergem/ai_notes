import pytest
import mongomock
from modules.note_crud import add_note, list_notes, edit_note, delete_note
from datetime import datetime

@pytest.fixture
def db():
    client = mongomock.MongoClient()
    return client['test_db']

def test_add_and_list_note(db):
    note_id = add_note(db, 'Test', 'Content', ['tag1'], 'work')
    notes = list_notes(db, {})
    assert len(notes) == 1
    assert notes[0]['_id'] == note_id
    assert notes[0]['title'] == 'Test'
    assert notes[0]['tags'] == ['tag1']
    assert notes[0]['workspace'] == 'work'

def test_edit_note(db):
    note_id = add_note(db, 'Test', 'Content', ['tag1'], 'work')
    count = edit_note(db, note_id, {'title': 'Updated', 'tags': ['tag2']})
    assert count == 1
    note = list_notes(db, {'_id': note_id})[0]
    assert note['title'] == 'Updated'
    assert note['tags'] == ['tag2']

def test_delete_note(db):
    note_id = add_note(db, 'Test', 'Content', ['tag1'], 'work')
    count = delete_note(db, note_id)
    assert count == 1
    notes = list_notes(db, {})
    assert len(notes) == 0 