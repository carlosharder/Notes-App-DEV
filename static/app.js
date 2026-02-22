/* Apple Notes — Client-Side Application */

(function () {
    'use strict';

    // --- State ---
    let currentSlug = null;
    let isEditing = false;
    let currentPage = 1;
    let currentQuery = '';
    let allLoaded = false;
    let loading = false;
    let saveTimeout = null;
    let noteTitles = [];
    let autocompleteIdx = -1;

    const PAGE_SIZE = 50;
    const AUTOSAVE_DELAY = 1500;
    const SEARCH_DEBOUNCE = 300;

    // --- DOM Refs ---
    const sidebar = document.getElementById('sidebar');
    const sidebarList = document.getElementById('sidebar-list');
    const sidebarSearch = document.getElementById('sidebar-search');
    const sidebarCount = document.getElementById('sidebar-count');
    const contentBody = document.getElementById('content-body');
    const editBtn = document.getElementById('edit-btn');
    const deleteBtn = document.getElementById('delete-btn');
    const saveIndicator = document.getElementById('save-indicator');
    const mobileBackBtn = document.getElementById('mobile-back-btn');
    const autocompleteEl = document.getElementById('link-autocomplete');

    // --- Sidebar Note Loading ---

    async function loadNotes(page, query, append) {
        if (loading) return;
        loading = true;

        const params = new URLSearchParams({ page, limit: PAGE_SIZE });
        if (query) params.set('q', query);

        try {
            const resp = await fetch('/api/notes?' + params);
            const data = await resp.json();

            if (!append) {
                sidebarList.innerHTML = '';
            }

            if (data.notes.length === 0 && !append) {
                sidebarList.innerHTML = '<div class="sidebar-empty">No notes found</div>';
            }

            data.notes.forEach(note => {
                const el = createNoteItem(note);
                sidebarList.appendChild(el);
            });

            if (data.notes.length < PAGE_SIZE) {
                allLoaded = true;
            }

            if (sidebarCount) {
                sidebarCount.textContent = data.total + ' note' + (data.total !== 1 ? 's' : '');
            }
        } catch (err) {
            console.error('Failed to load notes:', err);
        }

        loading = false;
    }

    function createNoteItem(note) {
        const el = document.createElement('div');
        el.className = 'note-item' + (note.slug === currentSlug ? ' active' : '');
        el.dataset.slug = note.slug;

        const shortDate = formatShortDate(note.modified);

        el.innerHTML =
            '<div class="note-item-title">' + escapeHtml(note.title) + '</div>' +
            '<div class="note-item-meta">' +
                '<span class="note-item-date">' + shortDate + '</span>' +
                '<span class="note-item-preview">' + escapeHtml(note.preview || '') + '</span>' +
            '</div>';

        el.addEventListener('click', () => {
            openNote(note.slug);
        });

        return el;
    }

    function formatShortDate(iso) {
        try {
            const dt = new Date(iso);
            const now = new Date();
            if (dt.toDateString() === now.toDateString()) {
                return dt.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
            }
            if (dt.getFullYear() === now.getFullYear()) {
                return dt.toLocaleDateString([], { month: 'short', day: 'numeric' });
            }
            return dt.toLocaleDateString([], { month: 'numeric', day: 'numeric', year: '2-digit' });
        } catch (e) {
            return iso;
        }
    }

    // Infinite scroll
    sidebarList.addEventListener('scroll', () => {
        if (allLoaded || loading) return;
        const { scrollTop, scrollHeight, clientHeight } = sidebarList;
        if (scrollTop + clientHeight >= scrollHeight - 100) {
            currentPage++;
            loadNotes(currentPage, currentQuery, true);
        }
    });

    // Search
    let searchTimeout;
    sidebarSearch.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentQuery = sidebarSearch.value.trim();
            currentPage = 1;
            allLoaded = false;
            loadNotes(1, currentQuery, false);
        }, SEARCH_DEBOUNCE);
    });

    // --- Note Operations ---

    async function openNote(slug) {
        if (isEditing && currentSlug) {
            await saveCurrentNote();
        }

        currentSlug = slug;
        isEditing = false;

        // Update URL without reload
        history.pushState({ slug }, '', '/notes/' + slug);

        // Mark active in sidebar
        document.querySelectorAll('.note-item').forEach(el => {
            el.classList.toggle('active', el.dataset.slug === slug);
        });

        // Show loading
        contentBody.innerHTML = '<div class="loading-spinner"></div>';
        updateToolbar();

        // Mobile: hide sidebar
        if (window.innerWidth <= 768) {
            sidebar.classList.add('hidden');
        }

        try {
            const resp = await fetch('/api/notes/' + slug);
            if (!resp.ok) throw new Error('Not found');
            const note = await resp.json();
            renderNoteView(note);
        } catch (err) {
            contentBody.innerHTML = '<div class="empty-state"><div class="empty-state-text">Note not found</div></div>';
        }
    }

    function renderNoteView(note) {
        contentBody.innerHTML =
            '<div class="note-view">' +
                '<h1 class="note-title-display">' + escapeHtml(note.title) + '</h1>' +
                '<div class="note-dates">' +
                    'Created ' + formatFullDate(note.created) +
                    ' &middot; Modified ' + formatFullDate(note.modified) +
                '</div>' +
                '<div class="note-content">' + note.html + '</div>' +
            '</div>';
        updateToolbar();
    }

    function renderNoteEditor(note) {
        contentBody.innerHTML =
            '<div class="note-editor">' +
                '<input type="text" class="note-title-input" id="editor-title" placeholder="Title" value="' + escapeAttr(note.title) + '">' +
                '<div class="editor-toolbar">' +
                    '<button type="button" id="toolbar-section" title="Section (large font)">' +
                        '<span style="font-size:16px;font-weight:700;">A</span>' +
                        ' Section' +
                    '</button>' +
                    '<button type="button" id="toolbar-subsection" title="Sub-Section (mid font)">' +
                        '<span style="font-size:14px;font-weight:600;">A</span>' +
                        ' Sub-Section' +
                    '</button>' +
                    '<button type="button" id="toolbar-text" title="Regular text">' +
                        '<span style="font-size:12px;">A</span>' +
                        ' Text' +
                    '</button>' +
                    '<span class="toolbar-divider"></span>' +
                    '<button type="button" id="toolbar-checklist" title="Insert checklist">' +
                        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>' +
                        ' Checklist' +
                    '</button>' +
                    '<button type="button" id="toolbar-link" title="Insert note link">' +
                        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>' +
                        ' Link' +
                    '</button>' +
                    '<span class="toolbar-divider"></span>' +
                    '<button type="button" id="toolbar-audio" title="Attach MP3 audio">' +
                        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>' +
                        ' Audio' +
                    '</button>' +
                '</div>' +
                '<textarea class="note-body-input" id="editor-body" placeholder="Start writing...">' + escapeHtml(note.body) + '</textarea>' +
            '</div>';

        const titleInput = document.getElementById('editor-title');
        const bodyInput = document.getElementById('editor-body');

        // Auto-save on input
        titleInput.addEventListener('input', scheduleAutosave);
        bodyInput.addEventListener('input', () => {
            scheduleAutosave();
            handleAutocomplete(bodyInput);
        });

        // Wiki-link autocomplete keyboard nav
        bodyInput.addEventListener('keydown', (e) => {
            if (autocompleteEl.classList.contains('visible')) {
                const items = autocompleteEl.querySelectorAll('.link-autocomplete-item');
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    autocompleteIdx = Math.min(autocompleteIdx + 1, items.length - 1);
                    updateAutocompleteSelection(items);
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    autocompleteIdx = Math.max(autocompleteIdx - 1, 0);
                    updateAutocompleteSelection(items);
                } else if (e.key === 'Enter' && autocompleteIdx >= 0) {
                    e.preventDefault();
                    insertAutocompleteSelection(bodyInput, items[autocompleteIdx].textContent);
                } else if (e.key === 'Escape') {
                    hideAutocomplete();
                }
            }
        });

        // Toolbar buttons
        document.getElementById('toolbar-section').addEventListener('click', () => {
            setLinePrefix(bodyInput, '[section] ');
        });
        document.getElementById('toolbar-subsection').addEventListener('click', () => {
            setLinePrefix(bodyInput, '[subsection] ');
        });
        document.getElementById('toolbar-text').addEventListener('click', () => {
            removeLinePrefix(bodyInput);
        });
        document.getElementById('toolbar-checklist').addEventListener('click', () => {
            insertAtCursor(bodyInput, '- [ ] ');
        });
        document.getElementById('toolbar-link').addEventListener('click', () => {
            insertAtCursor(bodyInput, '[[');
            bodyInput.focus();
            handleAutocomplete(bodyInput);
        });

        // Audio upload button
        document.getElementById('toolbar-audio').addEventListener('click', () => {
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = '.mp3,audio/mpeg';
            fileInput.style.display = 'none';
            document.body.appendChild(fileInput);

            fileInput.addEventListener('change', async () => {
                const file = fileInput.files[0];
                if (!file) return;

                // Show uploading indicator
                showSaveIndicator('saving');

                const formData = new FormData();
                formData.append('file', file);

                try {
                    const resp = await fetch('/api/notes/' + currentSlug + '/audio', {
                        method: 'POST',
                        body: formData,
                    });
                    if (!resp.ok) {
                        const err = await resp.json();
                        alert('Upload failed: ' + (err.error || 'Unknown error'));
                        showSaveIndicator('error');
                        return;
                    }
                    const data = await resp.json();

                    // Insert [audio:filename.mp3] at cursor
                    insertAtCursor(bodyInput, '[audio:' + data.filename + ']');
                    showSaveIndicator('saved');
                } catch (err) {
                    console.error('Audio upload failed:', err);
                    showSaveIndicator('error');
                }

                fileInput.remove();
            });

            fileInput.click();
        });

        bodyInput.focus();
        updateToolbar();
    }

    async function saveCurrentNote() {
        if (!currentSlug || !isEditing) return;

        const titleInput = document.getElementById('editor-title');
        const bodyInput = document.getElementById('editor-body');
        if (!titleInput || !bodyInput) return;

        const title = titleInput.value.trim() || 'Untitled';
        const body = bodyInput.value;

        showSaveIndicator('saving');

        try {
            const resp = await fetch('/api/notes/' + currentSlug, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, body }),
            });
            const data = await resp.json();

            // If slug changed, update state
            if (data.slug !== currentSlug) {
                currentSlug = data.slug;
                history.replaceState({ slug: data.slug }, '', '/notes/' + data.slug);
            }

            showSaveIndicator('saved');
            refreshSidebarNote(data.slug);
        } catch (err) {
            showSaveIndicator('error');
            console.error('Save failed:', err);
        }
    }

    function scheduleAutosave() {
        clearTimeout(saveTimeout);
        showSaveIndicator('editing');
        saveTimeout = setTimeout(saveCurrentNote, AUTOSAVE_DELAY);
    }

    async function createNewNote() {
        try {
            const resp = await fetch('/api/notes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: 'Untitled', body: '' }),
            });
            const data = await resp.json();

            // Reload sidebar and open the note in edit mode
            currentPage = 1;
            allLoaded = false;
            await loadNotes(1, currentQuery, false);
            currentSlug = data.slug;
            isEditing = true;

            // Fetch and show editor
            const noteResp = await fetch('/api/notes/' + data.slug);
            const note = await noteResp.json();
            renderNoteEditor(note);

            // Select the title for quick rename
            const titleInput = document.getElementById('editor-title');
            if (titleInput) {
                titleInput.select();
            }

            // Update URL
            history.pushState({ slug: data.slug }, '', '/notes/' + data.slug);

            // Mobile: hide sidebar
            if (window.innerWidth <= 768) {
                sidebar.classList.add('hidden');
            }

            // Mark active
            document.querySelectorAll('.note-item').forEach(el => {
                el.classList.toggle('active', el.dataset.slug === data.slug);
            });
        } catch (err) {
            console.error('Failed to create note:', err);
        }
    }

    async function deleteCurrentNote() {
        if (!currentSlug) return;

        // Show confirmation dialog
        const overlay = document.createElement('div');
        overlay.className = 'confirm-overlay';
        overlay.innerHTML =
            '<div class="confirm-dialog">' +
                '<h3>Delete Note?</h3>' +
                '<p>This action cannot be undone.</p>' +
                '<div class="confirm-dialog-actions">' +
                    '<button class="btn-secondary" id="confirm-cancel">Cancel</button>' +
                    '<button class="btn-danger" id="confirm-delete">Delete</button>' +
                '</div>' +
            '</div>';
        document.body.appendChild(overlay);

        return new Promise(resolve => {
            document.getElementById('confirm-cancel').addEventListener('click', () => {
                overlay.remove();
                resolve();
            });
            document.getElementById('confirm-delete').addEventListener('click', async () => {
                overlay.remove();
                try {
                    await fetch('/api/notes/' + currentSlug, { method: 'DELETE' });
                    currentSlug = null;
                    isEditing = false;
                    showEmptyState();
                    updateToolbar();
                    currentPage = 1;
                    allLoaded = false;
                    await loadNotes(1, currentQuery, false);
                } catch (err) {
                    console.error('Delete failed:', err);
                }
                resolve();
            });
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    overlay.remove();
                    resolve();
                }
            });
        });
    }

    function toggleEdit() {
        if (isEditing) {
            // Save and switch to view
            saveCurrentNote().then(() => {
                isEditing = false;
                openNote(currentSlug);
            });
        } else {
            // Switch to edit
            isEditing = true;
            fetch('/api/notes/' + currentSlug)
                .then(r => r.json())
                .then(note => renderNoteEditor(note));
        }
    }

    // --- Refresh sidebar item after save ---

    async function refreshSidebarNote(slug) {
        currentPage = 1;
        allLoaded = false;
        await loadNotes(1, currentQuery, false);
    }

    // --- Toolbar ---

    function updateToolbar() {
        if (!editBtn || !deleteBtn) return;

        if (currentSlug) {
            editBtn.style.display = '';
            deleteBtn.style.display = '';
            editBtn.title = isEditing ? 'Done' : 'Edit';
            editBtn.innerHTML = isEditing
                ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>'
                : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>';
        } else {
            editBtn.style.display = 'none';
            deleteBtn.style.display = 'none';
        }
    }

    function showSaveIndicator(state) {
        if (!saveIndicator) return;
        saveIndicator.className = 'save-indicator';
        if (state === 'saving') {
            saveIndicator.textContent = 'Saving...';
            saveIndicator.classList.add('saving');
        } else if (state === 'saved') {
            saveIndicator.textContent = 'Saved';
            saveIndicator.classList.add('saved');
            setTimeout(() => {
                if (saveIndicator.textContent === 'Saved') {
                    saveIndicator.textContent = '';
                }
            }, 2000);
        } else if (state === 'error') {
            saveIndicator.textContent = 'Save failed';
            saveIndicator.style.color = 'var(--danger)';
        } else {
            saveIndicator.textContent = '';
        }
    }

    function showEmptyState() {
        contentBody.innerHTML =
            '<div class="empty-state">' +
                '<div class="empty-state-icon">' +
                    '<svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/></svg>' +
                '</div>' +
                '<div class="empty-state-text">Select a note</div>' +
                '<div class="empty-state-sub">Choose a note from the sidebar or create a new one</div>' +
            '</div>';
    }

    // --- Checkbox Toggle ---

    document.addEventListener('change', (e) => {
        if (e.target.classList.contains('note-checkbox')) {
            const slug = e.target.dataset.slug;
            const line = parseInt(e.target.dataset.line);
            const checked = e.target.checked;

            fetch('/api/notes/' + slug + '/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ line, checked }),
            }).catch(err => console.error('Toggle failed:', err));

            // Strikethrough visual feedback
            const li = e.target.closest('li');
            if (li) {
                if (checked) {
                    li.style.color = 'var(--text-tertiary)';
                    li.style.textDecoration = 'line-through';
                } else {
                    li.style.color = '';
                    li.style.textDecoration = '';
                }
            }
        }
    });

    // Handle wiki-link clicks without page reload
    document.addEventListener('click', (e) => {
        const wikiLink = e.target.closest('.wiki-link[data-slug]');
        if (wikiLink) {
            e.preventDefault();
            openNote(wikiLink.dataset.slug);
        }
    });

    // --- Wiki-Link Autocomplete ---

    async function fetchTitles() {
        try {
            const resp = await fetch('/api/notes/titles');
            noteTitles = await resp.json();
        } catch (err) {
            console.error('Failed to fetch titles:', err);
        }
    }

    function handleAutocomplete(textarea) {
        const val = textarea.value;
        const cursor = textarea.selectionStart;
        const before = val.substring(0, cursor);

        // Check if we're inside [[ ... (no closing ]])
        const match = before.match(/\[\[([^\[\]]*)$/);
        if (match) {
            const query = match[1].toLowerCase();
            const filtered = noteTitles.filter(t =>
                t.title.toLowerCase().includes(query) && t.slug !== currentSlug
            ).slice(0, 8);

            if (filtered.length > 0) {
                showAutocomplete(textarea, filtered, cursor);
                return;
            }
        }

        hideAutocomplete();
    }

    function showAutocomplete(textarea, items, cursor) {
        autocompleteIdx = 0;

        autocompleteEl.innerHTML = '';
        items.forEach((item, i) => {
            const el = document.createElement('div');
            el.className = 'link-autocomplete-item' + (i === 0 ? ' selected' : '');
            el.textContent = item.title;
            el.addEventListener('click', () => {
                insertAutocompleteSelection(textarea, item.title);
            });
            autocompleteEl.appendChild(el);
        });

        // Position near the textarea (simplified: below toolbar area)
        const rect = textarea.getBoundingClientRect();
        autocompleteEl.style.left = (rect.left + 40) + 'px';
        autocompleteEl.style.top = (rect.top + 30) + 'px';
        autocompleteEl.classList.add('visible');
    }

    function hideAutocomplete() {
        autocompleteEl.classList.remove('visible');
        autocompleteIdx = -1;
    }

    function updateAutocompleteSelection(items) {
        items.forEach((el, i) => {
            el.classList.toggle('selected', i === autocompleteIdx);
        });
    }

    function insertAutocompleteSelection(textarea, title) {
        const val = textarea.value;
        const cursor = textarea.selectionStart;
        const before = val.substring(0, cursor);
        const after = val.substring(cursor);

        // Find the [[ and replace everything after it with the title]]
        const openBracket = before.lastIndexOf('[[');
        if (openBracket !== -1) {
            textarea.value = before.substring(0, openBracket) + '[[' + title + ']]' + after;
            const newPos = openBracket + title.length + 4; // [[ + title + ]]
            textarea.setSelectionRange(newPos, newPos);
        }

        hideAutocomplete();
        textarea.focus();
        scheduleAutosave();
    }

    // --- Editor Helpers ---

    function insertAtCursor(textarea, text) {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const val = textarea.value;

        // If at start of line or empty, just insert
        // Otherwise, add newline first
        let prefix = '';
        if (start > 0 && val[start - 1] !== '\n') {
            prefix = '\n';
        }

        textarea.value = val.substring(0, start) + prefix + text + val.substring(end);
        const newPos = start + prefix.length + text.length;
        textarea.setSelectionRange(newPos, newPos);
        textarea.focus();
        scheduleAutosave();
    }

    function setLinePrefix(textarea, prefix) {
        // Set or replace the prefix on the current line
        const start = textarea.selectionStart;
        const val = textarea.value;
        const lineStart = val.lastIndexOf('\n', start - 1) + 1;
        const lineEnd = val.indexOf('\n', start);
        const lineEndPos = lineEnd === -1 ? val.length : lineEnd;
        const line = val.substring(lineStart, lineEndPos);

        // Remove any existing prefix
        const stripped = line.replace(/^\[(section|subsection)\]\s*/i, '');
        const newLine = prefix + stripped;
        const diff = newLine.length - line.length;

        textarea.value = val.substring(0, lineStart) + newLine + val.substring(lineEndPos);
        textarea.setSelectionRange(start + diff, start + diff);
        textarea.focus();
        scheduleAutosave();
    }

    function removeLinePrefix(textarea) {
        // Remove [section] or [subsection] prefix from the current line
        const start = textarea.selectionStart;
        const val = textarea.value;
        const lineStart = val.lastIndexOf('\n', start - 1) + 1;
        const lineEnd = val.indexOf('\n', start);
        const lineEndPos = lineEnd === -1 ? val.length : lineEnd;
        const line = val.substring(lineStart, lineEndPos);

        const stripped = line.replace(/^\[(section|subsection)\]\s*/i, '');
        const diff = stripped.length - line.length;

        textarea.value = val.substring(0, lineStart) + stripped + val.substring(lineEndPos);
        const newPos = Math.max(lineStart, start + diff);
        textarea.setSelectionRange(newPos, newPos);
        textarea.focus();
        scheduleAutosave();
    }

    // --- Mobile Navigation ---

    if (mobileBackBtn) {
        mobileBackBtn.addEventListener('click', () => {
            if (isEditing) {
                saveCurrentNote();
            }
            sidebar.classList.remove('hidden');
            currentSlug = null;
            isEditing = false;
            showEmptyState();
            updateToolbar();
            history.pushState({}, '', '/notes');
        });
    }

    // Browser back/forward
    window.addEventListener('popstate', (e) => {
        if (e.state && e.state.slug) {
            openNote(e.state.slug);
        } else {
            currentSlug = null;
            isEditing = false;
            showEmptyState();
            updateToolbar();
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('hidden');
            }
        }
    });

    // --- Utility ---

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function escapeAttr(str) {
        return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function formatFullDate(iso) {
        try {
            const dt = new Date(iso);
            return dt.toLocaleDateString([], {
                year: 'numeric', month: 'long', day: 'numeric',
                hour: 'numeric', minute: '2-digit',
            });
        } catch (e) {
            return iso;
        }
    }

    // --- Button Bindings ---

    document.getElementById('new-note-btn').addEventListener('click', createNewNote);
    editBtn.addEventListener('click', toggleEdit);
    deleteBtn.addEventListener('click', deleteCurrentNote);

    // --- Keyboard shortcut ---
    document.addEventListener('keydown', (e) => {
        // Cmd/Ctrl+N: new note
        if ((e.metaKey || e.ctrlKey) && e.key === 'n') {
            e.preventDefault();
            createNewNote();
        }
        // Cmd/Ctrl+E: toggle edit
        if ((e.metaKey || e.ctrlKey) && e.key === 'e') {
            e.preventDefault();
            if (currentSlug) toggleEdit();
        }
        // Escape: exit edit or close autocomplete
        if (e.key === 'Escape') {
            if (autocompleteEl.classList.contains('visible')) {
                hideAutocomplete();
            } else if (isEditing) {
                toggleEdit();
            }
        }
    });

    // --- Init ---

    async function init() {
        await loadNotes(1, '', false);
        await fetchTitles();

        // If there's an initial slug (from URL), open it
        const initialSlug = document.body.dataset.initialSlug;
        if (initialSlug) {
            openNote(initialSlug);
        } else {
            showEmptyState();
        }
        updateToolbar();
    }

    init();

})();
