/* Apple Notes — Client-Side Application (WYSIWYG Editor) */

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

    // =====================================================================
    // WYSIWYG: Markup <-> Editable HTML converters
    // =====================================================================

    /**
     * Convert raw markup text to editable HTML blocks for contenteditable.
     * Each line becomes a <div> with data-block attribute.
     */
    function markupToEditableHTML(bodyText, slug) {
        if (!bodyText && bodyText !== '') return '<div class="note-line" data-block="text"><br></div>';

        const lines = bodyText.split('\n');
        const parts = [];

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const stripped = line.trim();

            // Section heading
            const sectionMatch = stripped.match(/^\[section\]\s*(.*)/i);
            if (sectionMatch) {
                const content = sectionMatch[1] || '';
                parts.push('<div class="note-section" data-block="section">' + renderInlineEditable(content) + (content ? '' : '<br>') + '</div>');
                continue;
            }

            // Sub-section heading
            const subsectionMatch = stripped.match(/^\[subsection\]\s*(.*)/i);
            if (subsectionMatch) {
                const content = subsectionMatch[1] || '';
                parts.push('<div class="note-subsection" data-block="subsection">' + renderInlineEditable(content) + (content ? '' : '<br>') + '</div>');
                continue;
            }

            // Checklist item (unchecked)
            const checkMatch = stripped.match(/^[-*]\s*\[ \]\s*(.*)/);
            if (checkMatch) {
                const content = checkMatch[1] || '';
                parts.push(
                    '<div class="note-check-item" data-block="check" data-checked="false">' +
                    '<input type="checkbox" class="note-checkbox-edit">' +
                    '<span class="check-text">' + renderInlineEditable(content) + (content ? '' : '<br>') + '</span></div>'
                );
                continue;
            }

            // Checklist item (checked)
            const checkxMatch = stripped.match(/^[-*]\s*\[x\]\s*(.*)/i);
            if (checkxMatch) {
                const content = checkxMatch[1] || '';
                parts.push(
                    '<div class="note-check-item checked" data-block="check" data-checked="true">' +
                    '<input type="checkbox" class="note-checkbox-edit" checked>' +
                    '<span class="check-text">' + renderInlineEditable(content) + (content ? '' : '<br>') + '</span></div>'
                );
                continue;
            }

            // Audio embed
            const audioMatch = stripped.match(/^\[audio:(.+?)\]$/i);
            if (audioMatch) {
                const filename = audioMatch[1].trim();
                parts.push(
                    '<div class="note-audio-block" data-block="audio" data-filename="' + escapeAttr(filename) + '" contenteditable="false">' +
                    '<div class="note-audio-name">' + escapeHtml(filename) + '</div>' +
                    '<audio controls preload="metadata">' +
                    '<source src="/api/audio/' + slug + '/' + encodeURIComponent(filename) + '" type="audio/mpeg">' +
                    '</audio></div>'
                );
                continue;
            }

            // Empty line
            if (!stripped) {
                parts.push('<div class="note-blank" data-block="blank"><br></div>');
                continue;
            }

            // Regular text
            parts.push('<div class="note-line" data-block="text">' + renderInlineEditable(stripped) + '</div>');
        }

        if (parts.length === 0) {
            return '<div class="note-line" data-block="text"><br></div>';
        }

        return parts.join('');
    }

    /**
     * Render inline content for editable blocks.
     * Converts [[wiki links]] to styled spans.
     */
    function renderInlineEditable(text) {
        if (!text) return '';
        // Escape HTML first
        let html = escapeHtml(text);
        // Replace [[Title]] with styled non-editable spans
        html = html.replace(/\[\[(.+?)\]\]/g, function(match, title) {
            return '<span class="wiki-link-edit" data-link-title="' + escapeAttr(title) + '" contenteditable="false">' + escapeHtml(title) + '</span>';
        });
        return html;
    }

    /**
     * Serialize contenteditable DOM back to markup text for storage.
     */
    function editableHTMLToMarkup(editorDiv) {
        const lines = [];
        const children = editorDiv.children;

        for (let i = 0; i < children.length; i++) {
            const block = children[i];
            const type = block.dataset.block || 'text';

            switch (type) {
                case 'section':
                    lines.push('[section] ' + getBlockText(block));
                    break;
                case 'subsection':
                    lines.push('[subsection] ' + getBlockText(block));
                    break;
                case 'check': {
                    const checked = block.querySelector('input[type="checkbox"]');
                    const marker = (checked && checked.checked) ? '- [x] ' : '- [ ] ';
                    const textEl = block.querySelector('.check-text');
                    lines.push(marker + getBlockText(textEl || block));
                    break;
                }
                case 'audio':
                    lines.push('[audio:' + (block.dataset.filename || '') + ']');
                    break;
                case 'blank':
                    lines.push('');
                    break;
                case 'text':
                default:
                    lines.push(getBlockText(block));
                    break;
            }
        }

        return lines.join('\n');
    }

    /**
     * Extract text from a block element, reconstructing [[wiki links]].
     */
    function getBlockText(el) {
        let text = '';
        for (let i = 0; i < el.childNodes.length; i++) {
            const node = el.childNodes[i];
            if (node.nodeType === Node.TEXT_NODE) {
                text += node.textContent;
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                if (node.classList && node.classList.contains('wiki-link-edit')) {
                    text += '[[' + (node.dataset.linkTitle || node.textContent) + ']]';
                } else if (node.tagName === 'BR') {
                    // skip trailing <br> in empty blocks
                } else if (node.tagName === 'INPUT') {
                    // skip checkbox inputs
                } else if (node.classList && node.classList.contains('check-text')) {
                    text += getBlockText(node);
                } else {
                    text += node.textContent;
                }
            }
        }
        return text;
    }

    // =====================================================================
    // WYSIWYG: Contenteditable helpers
    // =====================================================================

    /**
     * Get the block-level element (direct child of editorDiv) containing the cursor.
     */
    function getCurrentBlock(editorDiv) {
        const sel = window.getSelection();
        if (!sel.rangeCount) return null;
        let node = sel.anchorNode;
        if (!node) return null;
        // Walk up to find direct child of editorDiv
        while (node && node.parentNode !== editorDiv) {
            node = node.parentNode;
            if (!node) return null;
        }
        return (node && node.parentNode === editorDiv) ? node : null;
    }

    /**
     * Place cursor at the end of an element.
     */
    function placeCursorIn(element) {
        const range = document.createRange();
        const sel = window.getSelection();

        if (element.dataset.block === 'check') {
            const textSpan = element.querySelector('.check-text');
            if (textSpan) {
                range.selectNodeContents(textSpan);
                range.collapse(false);
                sel.removeAllRanges();
                sel.addRange(range);
                return;
            }
        }

        range.selectNodeContents(element);
        range.collapse(false);
        sel.removeAllRanges();
        sel.addRange(range);
    }

    /**
     * Place cursor at the start of an element.
     */
    function placeCursorAtStart(element) {
        const range = document.createRange();
        const sel = window.getSelection();

        if (element.dataset.block === 'check') {
            const textSpan = element.querySelector('.check-text');
            if (textSpan) {
                range.selectNodeContents(textSpan);
                range.collapse(true);
                sel.removeAllRanges();
                sel.addRange(range);
                return;
            }
        }

        range.selectNodeContents(element);
        range.collapse(true);
        sel.removeAllRanges();
        sel.addRange(range);
    }

    /**
     * Check if cursor is at the very start of a block.
     */
    function isAtBlockStart(block) {
        const sel = window.getSelection();
        if (!sel.rangeCount) return false;
        const range = sel.getRangeAt(0);
        if (!range.collapsed) return false;

        let container = range.startContainer;
        let offset = range.startOffset;

        // If cursor is in the block itself (not a child text node)
        if (container === block && offset === 0) return true;

        // For check items, check within .check-text
        const textContainer = (block.dataset.block === 'check')
            ? block.querySelector('.check-text')
            : block;

        if (!textContainer) return false;

        // Walk to find if there's any text before the cursor
        let foundText = false;
        function walkBefore(node) {
            if (node === container) {
                if (node.nodeType === Node.TEXT_NODE && offset > 0) foundText = true;
                return true; // stop
            }
            if (node.nodeType === Node.TEXT_NODE && node.textContent.length > 0) {
                foundText = true;
            }
            for (let i = 0; i < node.childNodes.length; i++) {
                if (node.childNodes[i].tagName === 'INPUT') continue; // skip checkbox
                if (walkBefore(node.childNodes[i])) return true;
            }
            return false;
        }
        walkBefore(textContainer);
        return !foundText;
    }

    /**
     * Create a new empty block of the given type.
     */
    function createBlock(type) {
        const div = document.createElement('div');
        switch (type) {
            case 'section':
                div.className = 'note-section';
                div.dataset.block = 'section';
                div.innerHTML = '<br>';
                break;
            case 'subsection':
                div.className = 'note-subsection';
                div.dataset.block = 'subsection';
                div.innerHTML = '<br>';
                break;
            case 'check':
                div.className = 'note-check-item';
                div.dataset.block = 'check';
                div.dataset.checked = 'false';
                div.innerHTML = '<input type="checkbox" class="note-checkbox-edit"><span class="check-text"><br></span>';
                break;
            case 'blank':
                div.className = 'note-blank';
                div.dataset.block = 'blank';
                div.innerHTML = '<br>';
                break;
            case 'text':
            default:
                div.className = 'note-line';
                div.dataset.block = 'text';
                div.innerHTML = '<br>';
                break;
        }
        return div;
    }

    // =====================================================================
    // Note Operations
    // =====================================================================

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

    // =====================================================================
    // WYSIWYG Editor
    // =====================================================================

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
                '<div class="note-body-editable" id="editor-body" contenteditable="true" data-placeholder="Start writing..."></div>' +
            '</div>';

        const titleInput = document.getElementById('editor-title');
        const editorBody = document.getElementById('editor-body');

        // Initialize with converted content
        editorBody.innerHTML = markupToEditableHTML(note.body, currentSlug);

        // Ensure at least one block exists
        ensureMinBlock(editorBody);

        // --- Autosave ---
        titleInput.addEventListener('input', scheduleAutosave);
        editorBody.addEventListener('input', function() {
            ensureMinBlock(editorBody);
            scheduleAutosave();
            handleAutocompleteEditable(editorBody);
        });

        // --- Keyboard handling ---
        editorBody.addEventListener('keydown', function(e) {
            // Autocomplete navigation
            if (autocompleteEl.classList.contains('visible')) {
                const items = autocompleteEl.querySelectorAll('.link-autocomplete-item');
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    autocompleteIdx = Math.min(autocompleteIdx + 1, items.length - 1);
                    updateAutocompleteSelection(items);
                    return;
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    autocompleteIdx = Math.max(autocompleteIdx - 1, 0);
                    updateAutocompleteSelection(items);
                    return;
                } else if (e.key === 'Enter' && autocompleteIdx >= 0) {
                    e.preventDefault();
                    insertAutocompleteLinkEditable(items[autocompleteIdx].textContent);
                    return;
                } else if (e.key === 'Escape') {
                    hideAutocomplete();
                    return;
                }
            }

            // Enter key
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleEnterKey(editorBody);
                return;
            }

            // Backspace at block start
            if (e.key === 'Backspace') {
                const block = getCurrentBlock(editorBody);
                if (block && isAtBlockStart(block)) {
                    e.preventDefault();
                    handleBackspaceAtStart(editorBody, block);
                    return;
                }
            }
        });

        // --- Paste handling ---
        editorBody.addEventListener('paste', function(e) {
            e.preventDefault();
            const text = e.clipboardData.getData('text/plain');
            handlePaste(editorBody, text);
        });

        // --- Checkbox toggle in editor ---
        editorBody.addEventListener('change', function(e) {
            if (e.target.classList.contains('note-checkbox-edit')) {
                const item = e.target.closest('[data-block="check"]');
                if (item) {
                    item.dataset.checked = e.target.checked ? 'true' : 'false';
                    if (e.target.checked) {
                        item.classList.add('checked');
                    } else {
                        item.classList.remove('checked');
                    }
                    scheduleAutosave();
                }
            }
        });

        // --- Toolbar buttons ---
        document.getElementById('toolbar-section').addEventListener('click', function() {
            setBlockType(editorBody, 'section');
            editorBody.focus();
        });
        document.getElementById('toolbar-subsection').addEventListener('click', function() {
            setBlockType(editorBody, 'subsection');
            editorBody.focus();
        });
        document.getElementById('toolbar-text').addEventListener('click', function() {
            setBlockType(editorBody, 'text');
            editorBody.focus();
        });
        document.getElementById('toolbar-checklist').addEventListener('click', function() {
            insertChecklistItem(editorBody);
        });
        document.getElementById('toolbar-link').addEventListener('click', function() {
            editorBody.focus();
            document.execCommand('insertText', false, '[[');
            handleAutocompleteEditable(editorBody);
        });

        // Audio upload button
        document.getElementById('toolbar-audio').addEventListener('click', function() {
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = '.mp3,audio/mpeg';
            fileInput.style.display = 'none';
            document.body.appendChild(fileInput);

            fileInput.addEventListener('change', async function() {
                const file = fileInput.files[0];
                if (!file) return;

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
                    insertAudioBlock(editorBody, currentSlug, data.filename);
                    showSaveIndicator('saved');
                    scheduleAutosave();
                } catch (err) {
                    console.error('Audio upload failed:', err);
                    showSaveIndicator('error');
                }

                fileInput.remove();
            });

            fileInput.click();
        });

        editorBody.focus();
        updateToolbar();
    }

    /**
     * Ensure editor has at least one block.
     */
    function ensureMinBlock(editorDiv) {
        if (editorDiv.children.length === 0) {
            editorDiv.appendChild(createBlock('text'));
        }
    }

    /**
     * Change the block type of the current block (section/subsection/text).
     */
    function setBlockType(editorDiv, type) {
        const block = getCurrentBlock(editorDiv);
        if (!block) return;
        if (block.dataset.block === 'audio') return; // don't convert audio

        // If it's a check item, convert to text-type block
        if (block.dataset.block === 'check') {
            const textSpan = block.querySelector('.check-text');
            const text = textSpan ? getBlockText(textSpan) : getBlockText(block);
            const cb = block.querySelector('input');
            if (cb) cb.remove();
            if (textSpan) {
                // Move text out of span
                while (textSpan.firstChild) {
                    block.insertBefore(textSpan.firstChild, textSpan);
                }
                textSpan.remove();
            }
            delete block.dataset.checked;
        }

        switch (type) {
            case 'section':
                block.className = 'note-section';
                block.dataset.block = 'section';
                break;
            case 'subsection':
                block.className = 'note-subsection';
                block.dataset.block = 'subsection';
                break;
            case 'text':
            default:
                block.className = 'note-line';
                block.dataset.block = 'text';
                break;
        }

        scheduleAutosave();
    }

    /**
     * Insert a new checklist item after the current block.
     */
    function insertChecklistItem(editorDiv) {
        const block = getCurrentBlock(editorDiv);
        const newBlock = createBlock('check');

        if (block && block.nextSibling) {
            editorDiv.insertBefore(newBlock, block.nextSibling);
        } else {
            editorDiv.appendChild(newBlock);
        }

        placeCursorIn(newBlock);
        editorDiv.focus();
        scheduleAutosave();
    }

    /**
     * Insert an audio block after the current block.
     */
    function insertAudioBlock(editorDiv, slug, filename) {
        const block = getCurrentBlock(editorDiv);
        const audioBlock = document.createElement('div');
        audioBlock.className = 'note-audio-block';
        audioBlock.dataset.block = 'audio';
        audioBlock.dataset.filename = filename;
        audioBlock.contentEditable = 'false';
        audioBlock.innerHTML =
            '<div class="note-audio-name">' + escapeHtml(filename) + '</div>' +
            '<audio controls preload="metadata">' +
            '<source src="/api/audio/' + slug + '/' + encodeURIComponent(filename) + '" type="audio/mpeg">' +
            '</audio>';

        if (block && block.nextSibling) {
            editorDiv.insertBefore(audioBlock, block.nextSibling);
        } else {
            editorDiv.appendChild(audioBlock);
        }

        // Add a blank line after audio for continued typing
        const afterBlock = createBlock('text');
        if (audioBlock.nextSibling) {
            editorDiv.insertBefore(afterBlock, audioBlock.nextSibling);
        } else {
            editorDiv.appendChild(afterBlock);
        }
        placeCursorIn(afterBlock);
    }

    // =====================================================================
    // Keyboard handlers
    // =====================================================================

    function handleEnterKey(editorDiv) {
        const block = getCurrentBlock(editorDiv);
        if (!block) {
            const newBlock = createBlock('text');
            editorDiv.appendChild(newBlock);
            placeCursorIn(newBlock);
            scheduleAutosave();
            return;
        }

        const blockType = block.dataset.block;

        // For checklist items
        if (blockType === 'check') {
            const textSpan = block.querySelector('.check-text');
            const text = textSpan ? getBlockText(textSpan).trim() : '';

            if (!text) {
                // Empty checklist → convert to regular text
                block.className = 'note-line';
                block.dataset.block = 'text';
                delete block.dataset.checked;
                const cb = block.querySelector('input');
                if (cb) cb.remove();
                const span = block.querySelector('.check-text');
                if (span) {
                    while (span.firstChild) block.insertBefore(span.firstChild, span);
                    span.remove();
                }
                block.innerHTML = '<br>';
                placeCursorIn(block);
                scheduleAutosave();
                return;
            }

            // Split check item at cursor and create new check item
            const sel = window.getSelection();
            const range = sel.getRangeAt(0);

            // Extract content after cursor within the text span
            const afterRange = document.createRange();
            afterRange.setStart(range.endContainer, range.endOffset);
            afterRange.setEndAfter(textSpan.lastChild || textSpan);
            const afterContent = afterRange.extractContents();

            // Clean up current block's text span
            if (!textSpan.textContent.trim() && !textSpan.querySelector('.wiki-link-edit')) {
                textSpan.innerHTML = '<br>';
            }

            // Create new checklist item with extracted content
            const newBlock = createBlock('check');
            const newTextSpan = newBlock.querySelector('.check-text');
            if (afterContent.textContent.trim() || afterContent.querySelector && afterContent.querySelector('.wiki-link-edit')) {
                newTextSpan.innerHTML = '';
                newTextSpan.appendChild(afterContent);
            }

            if (block.nextSibling) {
                editorDiv.insertBefore(newBlock, block.nextSibling);
            } else {
                editorDiv.appendChild(newBlock);
            }
            placeCursorAtStart(newBlock);
            scheduleAutosave();
            return;
        }

        // For audio blocks — just create a text block after
        if (blockType === 'audio') {
            const newBlock = createBlock('text');
            if (block.nextSibling) {
                editorDiv.insertBefore(newBlock, block.nextSibling);
            } else {
                editorDiv.appendChild(newBlock);
            }
            placeCursorIn(newBlock);
            scheduleAutosave();
            return;
        }

        // For section/subsection/text/blank — split at cursor
        const sel = window.getSelection();
        const range = sel.getRangeAt(0);

        // Extract content after cursor
        const afterRange = document.createRange();
        afterRange.setStart(range.endContainer, range.endOffset);
        if (block.lastChild) {
            afterRange.setEndAfter(block.lastChild);
        } else {
            afterRange.setEnd(block, block.childNodes.length);
        }
        const afterContent = afterRange.extractContents();

        // If original block is now empty, add <br>
        if (!block.textContent.trim() && !block.querySelector('.wiki-link-edit')) {
            block.innerHTML = '<br>';
        }

        // Create new block (always regular text for Enter)
        const newBlock = createBlock('text');
        if (afterContent.textContent.trim() || (afterContent.querySelector && afterContent.querySelector('.wiki-link-edit'))) {
            newBlock.innerHTML = '';
            newBlock.appendChild(afterContent);
        }

        if (block.nextSibling) {
            editorDiv.insertBefore(newBlock, block.nextSibling);
        } else {
            editorDiv.appendChild(newBlock);
        }
        placeCursorAtStart(newBlock);
        scheduleAutosave();
    }

    function handleBackspaceAtStart(editorDiv, block) {
        const blockType = block.dataset.block;

        // Checklist → convert to regular text
        if (blockType === 'check') {
            const textSpan = block.querySelector('.check-text');
            const frag = document.createDocumentFragment();
            if (textSpan) {
                while (textSpan.firstChild) frag.appendChild(textSpan.firstChild);
            }
            block.className = 'note-line';
            block.dataset.block = 'text';
            delete block.dataset.checked;
            block.innerHTML = '';
            if (frag.childNodes.length > 0 && !(frag.childNodes.length === 1 && frag.firstChild.tagName === 'BR')) {
                block.appendChild(frag);
            } else {
                block.innerHTML = '<br>';
            }
            placeCursorAtStart(block);
            scheduleAutosave();
            return;
        }

        // Section/subsection → convert to regular text
        if (blockType === 'section' || blockType === 'subsection') {
            block.className = 'note-line';
            block.dataset.block = 'text';
            scheduleAutosave();
            return;
        }

        // Regular text/blank → merge with previous block
        const prev = block.previousElementSibling;
        if (!prev) return; // first block, nothing to merge

        if (prev.dataset.block === 'audio') {
            // Can't merge into audio, just remove empty block
            if (!block.textContent.trim()) {
                block.remove();
                scheduleAutosave();
            }
            return;
        }

        // Get the target element to merge into
        let mergeTarget = prev;
        if (prev.dataset.block === 'check') {
            mergeTarget = prev.querySelector('.check-text') || prev;
        }

        // Remove <br> from target if it's the only content
        if (mergeTarget.innerHTML.trim() === '<br>') {
            mergeTarget.innerHTML = '';
        }

        const cursorOffset = mergeTarget.textContent.length;

        // Move all children from current block to end of target
        const frag = document.createDocumentFragment();
        while (block.firstChild) {
            if (block.firstChild.tagName === 'BR' && block.childNodes.length === 1) {
                block.removeChild(block.firstChild);
            } else {
                frag.appendChild(block.firstChild);
            }
        }
        mergeTarget.appendChild(frag);
        block.remove();

        // Place cursor at merge point
        placeCursorAtTextOffset(mergeTarget, cursorOffset);
        scheduleAutosave();
    }

    /**
     * Place cursor at a specific text offset within an element.
     */
    function placeCursorAtTextOffset(element, targetOffset) {
        const range = document.createRange();
        const sel = window.getSelection();
        let offset = 0;

        function walk(node) {
            if (node.nodeType === Node.TEXT_NODE) {
                if (offset + node.textContent.length >= targetOffset) {
                    range.setStart(node, targetOffset - offset);
                    range.collapse(true);
                    return true;
                }
                offset += node.textContent.length;
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                if (node.tagName === 'BR') return false;
                if (node.tagName === 'INPUT') return false;
                for (let i = 0; i < node.childNodes.length; i++) {
                    if (walk(node.childNodes[i])) return true;
                }
            }
            return false;
        }

        if (!walk(element)) {
            // Fallback: place at end
            range.selectNodeContents(element);
            range.collapse(false);
        }

        sel.removeAllRanges();
        sel.addRange(range);
    }

    /**
     * Handle paste: strip formatting and insert as plain text blocks.
     */
    function handlePaste(editorDiv, text) {
        if (!text) return;

        const lines = text.split('\n');

        if (lines.length === 1) {
            // Single line: just insert text
            document.execCommand('insertText', false, lines[0]);
            scheduleAutosave();
            return;
        }

        // Multi-line paste: insert first line at cursor, create blocks for rest
        document.execCommand('insertText', false, lines[0]);

        const block = getCurrentBlock(editorDiv);
        let insertAfter = block;

        for (let i = 1; i < lines.length; i++) {
            const newBlock = createBlock('text');
            if (lines[i].trim()) {
                newBlock.textContent = lines[i];
            }
            if (insertAfter && insertAfter.nextSibling) {
                editorDiv.insertBefore(newBlock, insertAfter.nextSibling);
            } else {
                editorDiv.appendChild(newBlock);
            }
            insertAfter = newBlock;
        }

        if (insertAfter) {
            placeCursorIn(insertAfter);
        }
        scheduleAutosave();
    }

    // =====================================================================
    // Wiki-Link Autocomplete (contenteditable version)
    // =====================================================================

    function handleAutocompleteEditable(editorDiv) {
        const sel = window.getSelection();
        if (!sel.rangeCount) { hideAutocomplete(); return; }

        const range = sel.getRangeAt(0);
        let textNode = range.startContainer;
        if (textNode.nodeType !== Node.TEXT_NODE) { hideAutocomplete(); return; }

        const textBefore = textNode.textContent.substring(0, range.startOffset);
        const match = textBefore.match(/\[\[([^\[\]]*)$/);

        if (match) {
            const query = match[1].toLowerCase();
            const filtered = noteTitles.filter(t =>
                t.title.toLowerCase().includes(query) && t.slug !== currentSlug
            ).slice(0, 8);

            if (filtered.length > 0) {
                showAutocompleteEditable(filtered);
                return;
            }
        }

        hideAutocomplete();
    }

    function showAutocompleteEditable(items) {
        autocompleteIdx = 0;
        autocompleteEl.innerHTML = '';

        items.forEach((item, i) => {
            const el = document.createElement('div');
            el.className = 'link-autocomplete-item' + (i === 0 ? ' selected' : '');
            el.textContent = item.title;
            el.addEventListener('mousedown', function(e) {
                e.preventDefault(); // prevent blur
                insertAutocompleteLinkEditable(item.title);
            });
            autocompleteEl.appendChild(el);
        });

        // Position near cursor
        const sel = window.getSelection();
        if (sel.rangeCount) {
            const r = sel.getRangeAt(0);
            const rect = r.getBoundingClientRect();
            autocompleteEl.style.left = rect.left + 'px';
            autocompleteEl.style.top = (rect.bottom + 4) + 'px';
        }

        autocompleteEl.classList.add('visible');
    }

    function insertAutocompleteLinkEditable(title) {
        const sel = window.getSelection();
        if (!sel.rangeCount) return;

        const range = sel.getRangeAt(0);
        const textNode = range.startContainer;
        if (textNode.nodeType !== Node.TEXT_NODE) return;

        const textBefore = textNode.textContent.substring(0, range.startOffset);
        const bracketPos = textBefore.lastIndexOf('[[');
        if (bracketPos === -1) return;

        const textAfter = textNode.textContent.substring(range.startOffset);
        const beforeText = textBefore.substring(0, bracketPos);

        // Create wiki-link span
        const linkSpan = document.createElement('span');
        linkSpan.className = 'wiki-link-edit';
        linkSpan.dataset.linkTitle = title;
        linkSpan.contentEditable = 'false';
        linkSpan.textContent = title;

        // Split and rebuild
        const parent = textNode.parentNode;
        textNode.textContent = beforeText;

        const afterNode = document.createTextNode('\u200B' + textAfter); // zero-width space for cursor
        parent.insertBefore(linkSpan, textNode.nextSibling);
        parent.insertBefore(afterNode, linkSpan.nextSibling);

        // Place cursor after the link
        const newRange = document.createRange();
        newRange.setStart(afterNode, 1); // after the zero-width space
        newRange.collapse(true);
        sel.removeAllRanges();
        sel.addRange(newRange);

        hideAutocomplete();
        scheduleAutosave();
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

    // =====================================================================
    // Save / Create / Delete / Toggle Edit
    // =====================================================================

    async function saveCurrentNote() {
        if (!currentSlug || !isEditing) return;

        const titleInput = document.getElementById('editor-title');
        const editorBody = document.getElementById('editor-body');
        if (!titleInput || !editorBody) return;

        const title = titleInput.value.trim() || 'Untitled';
        const body = editableHTMLToMarkup(editorBody);

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

            currentPage = 1;
            allLoaded = false;
            await loadNotes(1, currentQuery, false);
            currentSlug = data.slug;
            isEditing = true;

            const noteResp = await fetch('/api/notes/' + data.slug);
            const note = await noteResp.json();
            renderNoteEditor(note);

            const titleInput = document.getElementById('editor-title');
            if (titleInput) titleInput.select();

            history.pushState({ slug: data.slug }, '', '/notes/' + data.slug);

            if (window.innerWidth <= 768) {
                sidebar.classList.add('hidden');
            }

            document.querySelectorAll('.note-item').forEach(el => {
                el.classList.toggle('active', el.dataset.slug === data.slug);
            });
        } catch (err) {
            console.error('Failed to create note:', err);
        }
    }

    async function deleteCurrentNote() {
        if (!currentSlug) return;

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
            saveCurrentNote().then(() => {
                isEditing = false;
                openNote(currentSlug);
            });
        } else {
            isEditing = true;
            fetch('/api/notes/' + currentSlug)
                .then(r => r.json())
                .then(note => renderNoteEditor(note));
        }
    }

    // --- Refresh sidebar ---
    async function refreshSidebarNote(slug) {
        currentPage = 1;
        allLoaded = false;
        await loadNotes(1, currentQuery, false);
    }

    // --- Toolbar state ---
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

    // =====================================================================
    // View mode: Checkbox toggle + wiki-link click
    // =====================================================================

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

    document.addEventListener('click', (e) => {
        const wikiLink = e.target.closest('.wiki-link[data-slug]');
        if (wikiLink) {
            e.preventDefault();
            openNote(wikiLink.dataset.slug);
        }
    });

    // =====================================================================
    // Wiki-link title cache
    // =====================================================================

    async function fetchTitles() {
        try {
            const resp = await fetch('/api/notes/titles');
            noteTitles = await resp.json();
        } catch (err) {
            console.error('Failed to fetch titles:', err);
        }
    }

    // =====================================================================
    // Utility
    // =====================================================================

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

    // =====================================================================
    // Mobile Navigation
    // =====================================================================

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

    // =====================================================================
    // Button Bindings + Keyboard Shortcuts
    // =====================================================================

    document.getElementById('new-note-btn').addEventListener('click', createNewNote);
    editBtn.addEventListener('click', toggleEdit);
    deleteBtn.addEventListener('click', deleteCurrentNote);

    document.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'n') {
            e.preventDefault();
            createNewNote();
        }
        if ((e.metaKey || e.ctrlKey) && e.key === 'e') {
            e.preventDefault();
            if (currentSlug) toggleEdit();
        }
        if (e.key === 'Escape') {
            if (autocompleteEl.classList.contains('visible')) {
                hideAutocomplete();
            } else if (isEditing) {
                toggleEdit();
            }
        }
    });

    // =====================================================================
    // Init
    // =====================================================================

    async function init() {
        await loadNotes(1, '', false);
        await fetchTitles();

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
