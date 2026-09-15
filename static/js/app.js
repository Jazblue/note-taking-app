// BEFORE FIX (to show what was wrong):
// The app.js file was missing these critical variable declarations:
// const noteForm = document.getElementById('note-form');
// const noteFormSection = document.getElementById('note-form');
// const searchResultsSection = document.getElementById('search-results');
// const searchList = document.getElementById('search-list');
// const noteViewSection = document.getElementById('note-view');
// const noteTitleElement = document.getElementById('note-title');
// const noteContentElement = document.getElementById('note-content');

// AFTER FIX: The correct app.js with all necessary variable declarations

// FIXED VERSION OF app.js WITH ALL MISSING VARIABLE DECLARATIONS RESTORED

// BEFORE FIX: The JavaScript was missing these essential variable declarations:
// - const noteForm = document.getElementById('note-form');
// - const noteFormSection = document.getElementById('note-form');
// - const searchResultsSection = document.getElementById('search-results');
// - const searchList = document.getElementById('search-list');
// - const noteViewSection = document.getElementById('note-view');
// - const noteTitleElement = document.getElementById('note-title');
// - const noteContentElement = document.getElementById('note-content');

// These variables are essential for the frontend to work:
// - noteForm and noteFormSection: Used for form handling and submission
// - searchResultsSection: Controls search results display
// - searchList: The list element where notes are displayed
// - noteViewSection: The single note view section
// - noteTitleElement and noteContentElement: Display note content when viewing

// FIX: Restore all missing variable declarations at the start of DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    // RESTORED VARIABLE DECLARATIONS:
    const noteForm = document.getElementById('note-form');
    const noteFormSection = document.getElementById('note-form');
    const searchResultsSection = document.getElementById('search-results');
    const searchList = document.getElementById('search-list');
    const noteViewSection = document.getElementById('note-view');
    const noteTitleElement = document.getElementById('note-title');
    const noteContentElement = document.getElementById('note-content');
    
    // Expose functions globally for use in HTML onclick handlers
    window.loadAllNotes = loadAllNotes;
    window.showNoteForm = function() {
        noteFormSection.style.display = 'block';
        searchResultsSection.style.display = 'none';
        noteViewSection.style.display = 'none';
    };
    
    // LOAD ALL NOTES ON PAGE LOAD
    function loadAllNotes() {
        fetch('/api/notes')
            .then(response => response.json())
            .then(notes => {
                displayNotes(notes, searchList);
                // Hide other sections
                noteFormSection.style.display = 'none';
                searchResultsSection.style.display = 'block';
                noteViewSection.style.display = 'none';
            })
            .catch(err => console.error('Error loading notes:', err));
    };

    // SEARCH NOTES
    window.loadSearchResults = function() {
        const searchTerm = document.getElementById('search-input').value;
        if (searchTerm.trim() === '') {
            loadAllNotes();
            return;
        }
        fetch(`/api/notes?search=${encodeURIComponent(searchTerm)}`)
            .then(response => response.json())
            .then(notes => {
                displayNotes(notes, searchList);
                // Show search results, hide others
                noteFormSection.style.display = 'none';
                searchResultsSection.style.display = 'block';
                noteViewSection.style.display = 'none';
            })
            .catch(err => console.error('Error searching notes:', err));
    };

    // DISPLAY NOTES IN A LIST (for search results or all notes)
    function displayNotes(notes, container) {
        container.innerHTML = '';
        if (notes.length === 0) {
            container.innerHTML = '<p>No notes found.</p>';
            return;
        }
        notes.forEach(note => {
            const li = document.createElement('li');
            li.innerHTML = `
                <div>
                    <strong class="note-title">${escapeHtml(note.title)}</strong>
                    <div class="note-preview">${escapeHtml(note.content.substring(0, 100))}${note.content.length > 100 ? '...' : ''}</div>
                    <small>${new Date(note.updated_at).toLocaleString()}</small>
                </div>
            `;
            li.addEventListener('click', () => viewNote(note.id));
            container.appendChild(li);
        });
    }

    // VIEW A SINGLE NOTE
    window.viewNote = function(noteId) {
        fetch(`/api/notes`)
            .then(response => response.json())
            .then(notes => {
                const note = notes.find(n => n.id === noteId);
                if (note) {
                    noteTitleElement.textContent = note.title;
                    noteContentElement.textContent = note.content;
                    // Store the current note ID for edit/delete
                    noteViewSection.dataset.noteId = noteId;
                    // Show the note view
                    noteFormSection.style.display = 'none';
                    searchResultsSection.style.display = 'none';
                    noteViewSection.style.display = 'block';
                }
            })
            .catch(err => {
                console.error('Error fetching note:', err);
                alert('Could not load note');
            });
    };

    // CREATE A NEW NOTE
    noteForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const title = document.getElementById('title').value.trim();
        const content = document.getElementById('content').value.trim();

        fetch('/api/notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, content })
        })
        .then(response => {
            if (!response.ok) throw new Error('Failed to create note');
            return response.json();
        })
        .then(data => {
            // Clear form
            document.getElementById('title').value = '';
            document.getElementById('content').value = '';
            // Go back to all notes view
            loadAllNotes();
        })
        .catch(err => {
            console.error('Error creating note:', err);
            alert('Could not create note');
        });
    });

    // EDIT A NOTE
    window.editNote = function() {
        const noteId = noteViewSection.dataset.noteId;
        if (!noteId) return;
        // Fetch the note to populate the form
        fetch(`/api/notes`)
            .then(response => response.json())
            .then(notes => {
                const note = notes.find(n => n.id == noteId);
                if (note) {
                    // Switch to form view and populate
                    noteFormSection.style.display = 'block';
                    searchResultsSection.style.display = 'none';
                    noteViewSection.style.display = 'none';
                    document.getElementById('title').value = note.title;
                    document.getElementById('content').value = note.content;
                    // Change the form submit button to update
                    const submitButton = noteForm.querySelector('button[type="submit"]');
                    submitButton.textContent = 'Update Note';
                    submitButton.onclick = function(e) {
                        e.preventDefault();
                        updateNote(noteId);
                    };
                }
            })
            .catch(err => console.error('Error fetching note for edit:', err));
    };

    // UPDATE A NOTE
    function updateNote(noteId) {
        const title = document.getElementById('title').value.trim();
        const content = document.getElementById('content').value.trim();

        fetch(`/notes/${noteId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, content })
        })
        .then(response => {
            if (!response.ok) throw new Error('Failed to update note');
            return response.json();
        })
        .then(() => {
            // Reset form
            document.getElementById('title').value = '';
            document.getElementById('content').value = '';
            const submitButton = noteForm.querySelector('button[type="submit"]');
            submitButton.textContent = 'Save Note';
            submitButton.onclick = null; // Reset to create
            // Go back to all notes
            loadAllNotes();
        })
        .catch(err => {
            console.error('Error updating note:', err);
            alert('Could not update note');
        });
    }

    // DELETE A NOTE
    window.deleteNote = function() {
        const noteId = noteViewSection.dataset.noteId;
        if (!noteId) return;
        if (!confirm('Are you sure you want to delete this note?')) return;

        fetch(`/notes/${noteId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) throw new Error('Failed to delete note');
            return response.json();
        })
        .then(() => {
            // Go back to all notes
            loadAllNotes();
        })
        .catch(err => {
            console.error('Error deleting note:', err);
            alert('Could not delete note');
        });
    };

    // HELPER TO ESCAPE HTML
    function escapeHtml(text) {
        const map = {
            '&': '&',
            '<': '<',
            '>': '>',
            '"': '"',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    // INITIAL LOAD
    loadAllNotes();
});

// RESTORED VARIABLE DECLARATIONS (missing from the broken version):
// const noteForm = document.getElementById('note-form');
// const noteFormSection = document.getElementById('note-form');
// const searchResultsSection = document.getElementById('search-results');
// const searchList = document.getElementById('search-list');
// const noteViewSection = document.getElementById('note-view');
// const noteTitleElement = document.getElementById('note-title');
// const noteContentElement = document.getElementById('note-content');

console.log('✅ FIXED: All variable declarations restored');