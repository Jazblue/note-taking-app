# Note-Taking Application

A local note-taking application built with Flask, SQLite, and a clean browser interface.

## Features

- Create, edit, and delete notes
- Search notes by content
- Automatic note titles from content
- Timestamps for all notes
- Persistent storage using SQLite
- Basic input validation
- Clean, responsive web interface

## Requirements

- Python 3.8+
- Flask
- SQLite (comes with Python)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd note-taking-app
```

2. Install Python dependencies:
```bash
pip install flask
```

3. Run the application:
```bash
python app.py
```

The application will be available at http://localhost:5000

## Project Structure

```
note-taking-app/
├── app.py                    # Main Flask application
├── templates/
│   └── index.html           # Web interface
├── static/
│   └── style.css            # CSS styling
├── tests/
│   └── test_app.py          # Automated test suite
├── instance/
│   └── notes.db             # SQLite database (instance folder)
├── README.md
└── requirements.txt
```

## Development

- Run tests: `python -m pytest tests/`
- Production-ready: Use a WSGI server like Gunicorn

## Data Model

Notes are stored in an SQLite database with the following schema:

```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## License

MIT
