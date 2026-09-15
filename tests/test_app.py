import os
import tempfile
import pytest
from app import app as flask_app

@pytest.fixture
def client():
    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp()
    flask_app.config['DATABASE'] = db_path
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret-key'

    with flask_app.test_client() as client:
        with flask_app.app_context():
            # Initialize the database
            from app import init_db
            init_db()
        yield client

    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)

def test_index_page(client):
    """Test that the index page loads correctly."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Note-Taking App' in rv.data

def test_create_note(client):
    """Test creating a new note via the API."""
    # Test creating a note with title and content
    rv = client.post('/api/notes', 
                     json={'title': 'Test Note', 'content': 'This is a test note.'})
    assert rv.status_code == 201
    data = rv.get_json()
    assert 'id' in data
    assert data['title'] == 'Test Note'
    assert data['content'] == 'This is a test note.'

    # Test retrieving the note via the API list (since we don't have a single note API)
    rv = client.get('/api/notes')
    assert rv.status_code == 200
    notes = rv.get_json()
    # Find the note we just created
    created_note = next((n for n in notes if n['id'] == data['id']), None)
    assert created_note is not None
    assert created_note['title'] == 'Test Note'
    assert created_note['content'] == 'This is a test note.'

def test_search_notes(client):
    """Test searching for notes."""
    # Create two notes
    client.post('/api/notes', json={'title': 'First Note', 'content': 'Hello world'})
    client.post('/api/notes', json={'title': 'Second Note', 'content': 'Another test'})

    # Search for 'world'
    rv = client.get('/api/notes?search=world')
    assert rv.status_code == 200
    data = rv.get_json()
    assert len(data) == 1
    assert data[0]['title'] == 'First Note'

    # Search for 'test' (case-insensitive)
    rv = client.get('/api/notes?search=test')
    assert rv.status_code == 200
    data = rv.get_json()
    assert len(data) == 1  # Only the second note has 'test' in content
    assert data[0]['title'] == 'Second Note'

    # Search for empty string (should return all notes)
    rv = client.get('/api/notes?search=')
    assert rv.status_code == 200
    data = rv.get_json()
    assert len(data) == 2

def test_update_note(client):
    """Test updating a note."""
    # Create a note
    rv = client.post('/api/notes', json={'title': 'Old Title', 'content': 'Old content'})
    assert rv.status_code == 201
    note_id = rv.get_json()['id']

    # Update the note
    rv = client.put(f'/notes/{note_id}', 
                    json={'title': 'New Title', 'content': 'New content'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['message'] == 'Note updated successfully'

    # Check the update via the API list
    rv = client.get('/api/notes')
    assert rv.status_code == 200
    notes = rv.get_json()
    updated_note = next((n for n in notes if n['id'] == note_id), None)
    assert updated_note is not None
    assert updated_note['title'] == 'New Title'
    assert updated_note['content'] == 'New content'

def test_delete_note(client):
    """Test deleting a note."""
    # Create a note
    rv = client.post('/api/notes', json={'title': 'To Delete', 'content': 'Delete me'})
    assert rv.status_code == 201
    note_id = rv.get_json()['id']

    # Delete the note
    rv = client.delete(f'/notes/{note_id}')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['message'] == 'Note deleted successfully'

    # Try to get the deleted note via API list (should not be present)
    rv = client.get('/api/notes')
    assert rv.status_code == 200
    notes = rv.get_json()
    assert not any(n['id'] == note_id for n in notes)

def test_validation(client):
    """Test input validation."""
    # Test missing title
    rv = client.post('/api/notes', json={'title': '', 'content': 'Some content'})
    assert rv.status_code == 400
    data = rv.get_json()
    assert 'errors' in data
    assert any('Title is required' in error for error in data['errors'])

    # Test missing content
    rv = client.post('/api/notes', json={'title': 'Title', 'content': ''})
    assert rv.status_code == 400
    data = rv.get_json()
    assert any('Content is required' in error for error in data['errors'])

    # Test title too long
    long_title = 'x' * 101
    rv = client.post('/api/notes', json={'title': long_title, 'content': 'Content'})
    assert rv.status_code == 400
    data = rv.get_json()
    assert any('100 characters or less' in error for error in data['errors'])