from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os
from datetime import datetime
from functools import wraps
import re

app = Flask(__name__)
# SECURITY WARNING: Set SECRET_KEY via environment variable in production
# Example: export SECRET_KEY="your-secret-key-here"
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DATABASE'] = os.path.join(app.instance_path, 'notes.db')

# Ensure instance directory exists
os.makedirs(app.instance_path, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def validate_note_input(title, content):
    errors = []
    if not title or len(title.strip()) < 1:
        errors.append('Title is required')
    elif len(title) > 100:
        errors.append('Title must be 100 characters or less')
    
    if not content or len(content.strip()) < 1:
        errors.append('Content is required')
    
    return errors

def extract_title_from_content(content):
    if not content:
        return 'Untitled Note'
    
    # Try to get first line that looks like a title (not too long, not just a few words)
    lines = content.strip().split('\n')
    for line in lines[:3]:  # Check first 3 lines
        line = line.strip()
        if line and len(line.split()) >= 2 and len(line) <= 80:
            return line
    
    # If no good first line, use first 50 chars
    preview = content.strip().replace('\n', ' ')[:50]
    return preview + ('...' if len(content.strip()) > 50 else '')

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    
    conn = get_db_connection()
    if search_query:
        # Search in both title and content
        notes = conn.execute(
            'SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY updated_at DESC',
            (f'%{search_query}%', f'%{search_query}%')
        ).fetchall()
    else:
        notes = conn.execute('SELECT * FROM notes ORDER BY updated_at DESC').fetchall()
    conn.close()
    
    return render_template('index.html', notes=notes, search_query=search_query)

@app.route('/notes/<int:note_id>')
def view_note(note_id):
    conn = get_db_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    conn.close()
    
    if note is None:
        return 'Note not found', 404
    
    return render_template('index.html', notes=[note], view_mode='single')

@app.route('/notes', methods=['POST'])
def create_note():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    title = data.get('title', '')
    content = data.get('content', '')
    
    errors = validate_note_input(title, content)
    if errors:
        return jsonify({'errors': errors}), 400
    
    if not title:
        title = extract_title_from_content(content)
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO notes (title, content) VALUES (?, ?)',
        (title, content)
    )
    conn.commit()
    note_id = conn.execute('SELECT last_insert_rowid()').fetchone()['last_insert_rowid()']
    conn.close()
    
    return jsonify({'id': note_id, 'message': 'Note created successfully'}), 201

@app.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    title = data.get('title', '')
    content = data.get('content', '')
    
    errors = validate_note_input(title, content)
    if errors:
        return jsonify({'errors': errors}), 400
    
    conn = get_db_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    
    if note is None:
        conn.close()
        return 'Note not found', 404
    
    conn.execute(
        'UPDATE notes SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (title, content, note_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Note updated successfully'})

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    conn = get_db_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    
    if note is None:
        conn.close()
        return 'Note not found', 404
    
    conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Note deleted successfully'})

@app.route('/api/notes')
def api_list_notes():
    search_query = request.args.get('search', '')
    
    conn = get_db_connection()
    if search_query:
        notes = conn.execute(
            'SELECT id, title, content, created_at, updated_at FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY updated_at DESC',
            (f'%{search_query}%', f'%{search_query}%')
        ).fetchall()
    else:
        notes = conn.execute('SELECT id, title, content, created_at, updated_at FROM notes ORDER BY updated_at DESC').fetchall()
    conn.close()
    
    notes_list = []
    for note in notes:
        notes_list.append({
            'id': note['id'],
            'title': note['title'],
            'content': note['content'],
            'created_at': note['created_at'],
            'updated_at': note['updated_at']
        })
    
    return jsonify(notes_list)

@app.route('/api/notes', methods=['POST'])
def api_create_note():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    title = data.get('title', '')
    content = data.get('content', '')
    
    errors = validate_note_input(title, content)
    if errors:
        return jsonify({'errors': errors}), 400
    
    if not title:
        title = extract_title_from_content(content)
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO notes (title, content) VALUES (?, ?)',
        (title, content)
    )
    conn.commit()
    note_id = conn.execute('SELECT last_insert_rowid()').fetchone()['last_insert_rowid()']
    conn.close()
    
    return jsonify({'id': note_id, 'title': title, 'content': content}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
