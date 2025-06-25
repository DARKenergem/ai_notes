import pytest
import mongomock
from modules.agent_runner import run_agents
from modules.agent_runner import action_functions
import types

@pytest.fixture
def db():
    client = mongomock.MongoClient()
    db = client['test_db']
    db['notes'].insert_one({'_id': 1, 'title': 'Test', 'content': 'Content', 'tags': ['reminder'], 'workspace': 'work'})
    return db

def test_calendar_event_agent(monkeypatch, db):
    called = {}
    def fake_calendar(db, note):
        called['calendar'] = True
    monkeypatch.setitem(action_functions, 'calendar_event', fake_calendar)
    note = db['notes'].find_one({'_id': 1})
    run_agents(db, note)
    assert called.get('calendar') 