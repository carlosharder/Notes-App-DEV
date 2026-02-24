import os
import re
import glob
import json
from datetime import datetime
from markupsafe import escape as html_escape
import shutil
from flask import (
    Flask, render_template, request, redirect, url_for, abort, flash, jsonify,
    send_from_directory,
)
from werkzeug.utils import secure_filename
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user,
)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB upload limit

NOTES_DIR = os.environ.get(
    'NOTES_DIR',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notes'),
)
os.makedirs(NOTES_DIR, exist_ok=True)

INDEX_PATH = os.path.join(NOTES_DIR, '.notes_index.json')

# --- Authentication ---

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

AUTH_USERNAME = os.environ.get('APP_USERNAME', 'carlosharder')
AUTH_PASSWORD_HASH = os.environ.get(
    'PASSWORD_HASH', generate_password_hash('#2cats', method='pbkdf2:sha256')
)


class User(UserMixin):
    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(user_id):
    if user_id == AUTH_USERNAME:
        return User(user_id)
    return None


# --- Helpers ---

def slugify(title):
    slug = title.lower().strip()
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug or 'untitled'


def unique_slug(title, exclude_slug=None):
    base = slugify(title)
    existing = set(_notes_cache.keys())
    if exclude_slug:
        existing.discard(exclude_slug)
    if base not in existing:
        return base
    n = 2
    while f'{base}-{n}' in existing:
        n += 1
    return f'{base}-{n}'


def parse_note(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    slug = os.path.splitext(os.path.basename(filepath))[0]
    title = slug
    created = modified = datetime.now().isoformat(timespec='seconds')
    body = content

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            front = parts[1].strip()
            body = parts[2].strip()
            for line in front.splitlines():
                if ':' in line:
                    key, val = line.split(':', 1)
                    key, val = key.strip(), val.strip()
                    if key == 'title':
                        title = val
                    elif key == 'created':
                        created = val
                    elif key == 'modified':
                        modified = val

    return {
        'slug': slug,
        'title': title,
        'created': created,
        'modified': modified,
        'body': body,
    }


def write_note(slug, title, body, created, modified):
    filepath = os.path.join(NOTES_DIR, f'{slug}.md')
    front = f'---\ntitle: {title}\ncreated: {created}\nmodified: {modified}\n---\n\n'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(front + body)


def preview_text(body, length=120):
    text = re.sub(r'[#*`>\[\]!_~\-]', '', body)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > length:
        return text[:length] + '...'
    return text


def format_date(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime('%b %d, %Y %H:%M')
    except (ValueError, TypeError):
        return iso_str


def short_date(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str)
        now = datetime.now()
        if dt.date() == now.date():
            return dt.strftime('%I:%M %p').lstrip('0')
        elif dt.year == now.year:
            return dt.strftime('%b %d')
        else:
            return dt.strftime('%m/%d/%y')
    except (ValueError, TypeError):
        return iso_str


app.jinja_env.filters['format_date'] = format_date
app.jinja_env.filters['short_date'] = short_date
app.jinja_env.filters['preview'] = preview_text


# --- Metadata Index ---

_notes_cache = {}


def load_index():
    global _notes_cache
    if os.path.exists(INDEX_PATH):
        try:
            with open(INDEX_PATH, 'r') as f:
                data = json.load(f)
            _notes_cache = data.get('notes', {})
        except (json.JSONDecodeError, IOError):
            rebuild_index()
    else:
        rebuild_index()


def rebuild_index():
    global _notes_cache
    _notes_cache = {}
    for filepath in glob.glob(os.path.join(NOTES_DIR, '*.md')):
        note = parse_note(filepath)
        _notes_cache[note['slug']] = {
            'title': note['title'],
            'slug': note['slug'],
            'created': note['created'],
            'modified': note['modified'],
            'preview': preview_text(note['body']),
        }
    save_index()


def save_index():
    try:
        with open(INDEX_PATH, 'w') as f:
            json.dump({'version': 1, 'notes': _notes_cache}, f)
    except IOError:
        pass


def update_index_entry(slug, title, created, modified, body):
    _notes_cache[slug] = {
        'title': title,
        'slug': slug,
        'created': created,
        'modified': modified,
        'preview': preview_text(body),
    }
    save_index()


def remove_index_entry(slug):
    _notes_cache.pop(slug, None)
    save_index()


# --- Plain-Text Rendering ---
# Notes are stored as plain text (no markdown). Special line prefixes:
#   [section] Text      -> large heading
#   [subsection] Text   -> mid-size heading
#   - [ ] / - [x]       -> checklist items
#   [[Note Title]]       -> inter-note link

def render_note(text, slug=None):
    title_map = {m['title'].lower(): m['slug'] for m in _notes_cache.values()}

    def resolve_hyperlinks(line_html):
        """Convert [text](url) to <a> tags with target=_blank, operating on already-escaped HTML."""
        def replace_hyperlink(match):
            text = match.group(1)
            url = match.group(2)
            # text and url are already HTML-escaped from the line_html
            return f'<a href="{url}" class="hyperlink" target="_blank" rel="noopener noreferrer">{text}</a>'
        return re.sub(r'\[(.+?)\]\((https?://[^\s)]+)\)', replace_hyperlink, line_html)

    def resolve_wiki_links(line_html):
        def replace_link(match):
            title = match.group(1)
            target_slug = title_map.get(title.lower())
            if target_slug:
                return f'<a href="/notes/{target_slug}" class="wiki-link" data-slug="{target_slug}">{html_escape(title)}</a>'
            return f'<span class="wiki-link broken">{html_escape(title)}</span>'
        return re.sub(r'\[\[(.+?)\]\]', replace_link, line_html)

    def resolve_inline_formatting(line_html):
        """Convert **bold**, *italic*, __underline__, ~~strike~~ to HTML tags."""
        line_html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line_html)
        line_html = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', line_html)
        line_html = re.sub(r'__(.+?)__', r'<u>\1</u>', line_html)
        line_html = re.sub(r'~~(.+?)~~', r'<s>\1</s>', line_html)
        return line_html

    def resolve_inline(line_html):
        """Apply all inline transformations: hyperlinks, wiki links, then formatting."""
        line_html = resolve_hyperlinks(line_html)
        line_html = resolve_wiki_links(line_html)
        line_html = resolve_inline_formatting(line_html)
        return line_html

    lines = text.split('\n')
    html_parts = []
    in_checklist = False
    in_bullet = False
    in_dash = False
    in_num = False

    def close_all_lists():
        nonlocal in_checklist, in_bullet, in_dash, in_num
        if in_checklist:
            html_parts.append('</ul>')
            in_checklist = False
        if in_bullet:
            html_parts.append('</ul>')
            in_bullet = False
        if in_dash:
            html_parts.append('</ul>')
            in_dash = False
        if in_num:
            html_parts.append('</ol>')
            in_num = False

    for i, line in enumerate(lines):
        indent_match = re.match(r'^(\t*)(.*)', line)
        indent_level = len(indent_match.group(1)) if indent_match else 0
        stripped = (indent_match.group(2) if indent_match else line).strip()
        indent_style = f' style="margin-left:{indent_level * 28}px"' if indent_level > 0 else ''

        # Section heading
        section_match = re.match(r'^\[section\]\s*(.*)', stripped, re.IGNORECASE)
        if section_match:
            close_all_lists()
            content = str(html_escape(section_match.group(1)))
            content = resolve_inline(content)
            html_parts.append(f'<div class="note-section"{indent_style}>{content}</div>')
            continue

        # Sub-section heading
        subsection_match = re.match(r'^\[subsection\]\s*(.*)', stripped, re.IGNORECASE)
        if subsection_match:
            close_all_lists()
            content = str(html_escape(subsection_match.group(1)))
            content = resolve_inline(content)
            html_parts.append(f'<div class="note-subsection"{indent_style}>{content}</div>')
            continue

        # Monospaced block
        mono_match = re.match(r'^\[mono\]\s*(.*)', stripped, re.IGNORECASE)
        if mono_match:
            close_all_lists()
            content = str(html_escape(mono_match.group(1)))
            content = resolve_inline(content)
            html_parts.append(f'<div class="note-mono"{indent_style}>{content}</div>')
            continue

        # Block Quote
        quote_match = re.match(r'^\[quote\]\s*(.*)', stripped, re.IGNORECASE)
        if quote_match:
            close_all_lists()
            content = str(html_escape(quote_match.group(1)))
            content = resolve_inline(content)
            html_parts.append(f'<div class="note-quote"{indent_style}>{content}</div>')
            continue

        # Checklist item (unchecked)
        check_match = re.match(r'^[-*]\s*\[ \]\s*(.*)', stripped)
        if check_match:
            if in_bullet: html_parts.append('</ul>'); in_bullet = False
            if in_dash: html_parts.append('</ul>'); in_dash = False
            if in_num: html_parts.append('</ol>'); in_num = False
            if not in_checklist:
                html_parts.append('<ul class="note-checklist">')
                in_checklist = True
            content = str(html_escape(check_match.group(1)))
            content = resolve_inline(content)
            html_parts.append(
                f'<li{indent_style}><input type="checkbox" class="note-checkbox" data-slug="{slug}" data-line="{i}">'
                f' {content}</li>'
            )
            continue

        # Checklist item (checked)
        checkx_match = re.match(r'^[-*]\s*\[x\]\s*(.*)', stripped, re.IGNORECASE)
        if checkx_match:
            if in_bullet: html_parts.append('</ul>'); in_bullet = False
            if in_dash: html_parts.append('</ul>'); in_dash = False
            if in_num: html_parts.append('</ol>'); in_num = False
            if not in_checklist:
                html_parts.append('<ul class="note-checklist">')
                in_checklist = True
            content = str(html_escape(checkx_match.group(1)))
            content = resolve_inline(content)
            html_parts.append(
                f'<li class="checked"{indent_style}><input type="checkbox" class="note-checkbox" data-slug="{slug}" data-line="{i}" checked>'
                f' {content}</li>'
            )
            continue

        # Bullet list item
        bullet_match = re.match(r'^\[bullet\]\s*(.*)', stripped, re.IGNORECASE)
        if bullet_match:
            if in_checklist:
                html_parts.append('</ul>')
                in_checklist = False
            if in_dash:
                html_parts.append('</ul>')
                in_dash = False
            if in_num:
                html_parts.append('</ol>')
                in_num = False
            if not in_bullet:
                html_parts.append('<ul class="note-bullet-list">')
                in_bullet = True
            content = str(html_escape(bullet_match.group(1)))
            content = resolve_inline(content)
            html_parts.append(f'<li{indent_style}>{content}</li>')
            continue

        # Dashed list item
        dash_match = re.match(r'^\[dash\]\s*(.*)', stripped, re.IGNORECASE)
        if dash_match:
            if in_checklist:
                html_parts.append('</ul>')
                in_checklist = False
            if in_bullet:
                html_parts.append('</ul>')
                in_bullet = False
            if in_num:
                html_parts.append('</ol>')
                in_num = False
            if not in_dash:
                html_parts.append('<ul class="note-dash-list">')
                in_dash = True
            content = str(html_escape(dash_match.group(1)))
            content = resolve_inline(content)
            html_parts.append(f'<li{indent_style}>{content}</li>')
            continue

        # Numbered list item
        num_match = re.match(r'^\[num\]\s*(.*)', stripped, re.IGNORECASE)
        if num_match:
            if in_checklist:
                html_parts.append('</ul>')
                in_checklist = False
            if in_bullet:
                html_parts.append('</ul>')
                in_bullet = False
            if in_dash:
                html_parts.append('</ul>')
                in_dash = False
            if not in_num:
                html_parts.append('<ol class="note-num-list">')
                in_num = True
            content = str(html_escape(num_match.group(1)))
            content = resolve_inline(content)
            html_parts.append(f'<li{indent_style}>{content}</li>')
            continue

        # Image embed: ![alt](images/filename.ext)
        img_match = re.match(r'^!\[([^\]]*)\]\((images/[^)]+)\)$', stripped)
        if img_match:
            close_all_lists()
            alt_text = str(html_escape(img_match.group(1)))
            img_filename = os.path.basename(img_match.group(2))
            safe_img = str(html_escape(img_filename))
            html_parts.append(
                f'<div class="note-image">'
                f'<img src="/api/images/{safe_img}" alt="{alt_text}" loading="lazy">'
                f'</div>'
            )
            continue

        # Audio embed
        audio_match = re.match(r'^\[audio:(.+?)\]$', stripped, re.IGNORECASE)
        if audio_match:
            close_all_lists()
            filename = audio_match.group(1).strip()
            safe_name = str(html_escape(filename))
            html_parts.append(
                f'<div class="note-audio">'
                f'<div class="note-audio-name">{safe_name}</div>'
                f'<audio controls preload="metadata">'
                f'<source src="/api/audio/{slug}/{filename}" type="audio/mpeg">'
                f'Your browser does not support audio playback.'
                f'</audio></div>'
            )
            continue

        # Close any open list containers
        close_all_lists()

        # Empty line -> paragraph break
        if not stripped:
            html_parts.append(f'<div class="note-blank"{indent_style}></div>')
            continue

        # Regular text line
        content = str(html_escape(stripped))
        content = resolve_inline(content)
        html_parts.append(f'<div class="note-line"{indent_style}>{content}</div>')

    close_all_lists()

    return '\n'.join(html_parts)


# --- Context Processor ---

@app.context_processor
def inject_sidebar_data():
    return dict(sidebar_notes=[])


# --- Auth Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('app_shell'))
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == AUTH_USERNAME and check_password_hash(AUTH_PASSWORD_HASH, password):
            login_user(User(username))
            return redirect(url_for('app_shell'))
        flash('Invalid username or password.')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# --- Main App Route ---

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('app_shell'))
    return redirect(url_for('login'))


@app.route('/notes')
@login_required
def app_shell():
    return render_template('base.html')


@app.route('/notes/<slug>')
@login_required
def note_view(slug):
    return render_template('base.html', initial_slug=slug)


@app.route('/service-worker.js')
def service_worker():
    return send_from_directory(app.static_folder, 'service-worker.js',
                               mimetype='application/javascript')


# --- API Routes ---

@app.route('/api/notes')
@login_required
def api_notes_list():
    q = request.args.get('q', '').strip().lower()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 50))

    notes = sorted(_notes_cache.values(), key=lambda n: n['modified'], reverse=True)

    if q:
        # Search in cache first (title + preview)
        filtered = [
            n for n in notes
            if q in n['title'].lower() or q in n['preview'].lower()
        ]
        # If few results, also search full body
        if len(filtered) < 5:
            cached_slugs = {n['slug'] for n in filtered}
            for n in notes:
                if n['slug'] not in cached_slugs:
                    filepath = os.path.join(NOTES_DIR, f"{n['slug']}.md")
                    if os.path.isfile(filepath):
                        note = parse_note(filepath)
                        if q in note['body'].lower():
                            filtered.append(n)
        notes = filtered

    total = len(notes)
    start = (page - 1) * limit
    end = start + limit

    return jsonify({
        'notes': notes[start:end],
        'total': total,
        'page': page,
    })


@app.route('/api/notes/<slug>')
@login_required
def api_note_get(slug):
    filepath = os.path.join(NOTES_DIR, f'{slug}.md')
    if not os.path.isfile(filepath):
        return jsonify({'error': 'not found'}), 404
    note = parse_note(filepath)
    html = render_note(note['body'], slug)
    return jsonify({
        'slug': note['slug'],
        'title': note['title'],
        'body': note['body'],
        'html': html,
        'created': note['created'],
        'modified': note['modified'],
    })


@app.route('/api/notes', methods=['POST'])
@login_required
def api_note_create():
    data = request.get_json()
    title = (data.get('title') or '').strip() or 'Untitled'
    body = data.get('body', '')
    slug = unique_slug(title)
    now = datetime.now().isoformat(timespec='seconds')
    write_note(slug, title, body, now, now)
    update_index_entry(slug, title, now, now, body)
    return jsonify({'slug': slug, 'title': title}), 201


@app.route('/api/notes/<slug>', methods=['PUT'])
@login_required
def api_note_update(slug):
    filepath = os.path.join(NOTES_DIR, f'{slug}.md')
    if not os.path.isfile(filepath):
        return jsonify({'error': 'not found'}), 404

    note = parse_note(filepath)
    data = request.get_json()
    title = (data.get('title') or '').strip() or note['title']
    body = data.get('body', note['body'])
    now = datetime.now().isoformat(timespec='seconds')

    new_slug = unique_slug(title, exclude_slug=slug)
    if new_slug != slug:
        os.remove(filepath)
        remove_index_entry(slug)
        # Rename media directory if it exists
        old_media = os.path.join(NOTES_DIR, 'media', slug)
        new_media = os.path.join(NOTES_DIR, 'media', new_slug)
        if os.path.isdir(old_media):
            os.makedirs(os.path.dirname(new_media), exist_ok=True)
            os.rename(old_media, new_media)

    write_note(new_slug, title, body, note['created'], now)
    update_index_entry(new_slug, title, note['created'], now, body)

    return jsonify({'slug': new_slug, 'title': title})


@app.route('/api/notes/<slug>', methods=['DELETE'])
@login_required
def api_note_delete(slug):
    filepath = os.path.join(NOTES_DIR, f'{slug}.md')
    if os.path.isfile(filepath):
        os.remove(filepath)
    # Also delete any attached audio files
    media_dir = os.path.join(NOTES_DIR, 'media', slug)
    if os.path.isdir(media_dir):
        shutil.rmtree(media_dir)
    remove_index_entry(slug)
    return jsonify({'ok': True})


@app.route('/api/notes/<slug>/toggle', methods=['POST'])
@login_required
def api_toggle_checkbox(slug):
    filepath = os.path.join(NOTES_DIR, f'{slug}.md')
    if not os.path.isfile(filepath):
        return jsonify({'error': 'not found'}), 404

    data = request.get_json()
    line_num = data.get('line')
    checked = data.get('checked')

    note = parse_note(filepath)
    lines = note['body'].split('\n')

    if 0 <= line_num < len(lines):
        if checked:
            lines[line_num] = re.sub(r'\[ \]', '[x]', lines[line_num], count=1)
        else:
            lines[line_num] = re.sub(r'\[x\]', '[ ]', lines[line_num], count=1)

    new_body = '\n'.join(lines)
    now = datetime.now().isoformat(timespec='seconds')
    write_note(slug, note['title'], new_body, note['created'], now)
    update_index_entry(slug, note['title'], note['created'], now, new_body)

    return jsonify({'ok': True})


@app.route('/api/notes/titles')
@login_required
def api_note_titles():
    titles = [
        {'title': m['title'], 'slug': m['slug']}
        for m in _notes_cache.values()
    ]
    titles.sort(key=lambda t: t['title'].lower())
    return jsonify(titles)


# --- Audio API ---

ALLOWED_AUDIO_EXT = {'.mp3'}


@app.route('/api/notes/<slug>/audio', methods=['POST'])
@login_required
def api_audio_upload(slug):
    """Upload an MP3 file attached to a note."""
    filepath = os.path.join(NOTES_DIR, f'{slug}.md')
    if not os.path.isfile(filepath):
        return jsonify({'error': 'Note not found'}), 404

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    f = request.files['file']
    if not f.filename:
        return jsonify({'error': 'Empty filename'}), 400

    filename = secure_filename(f.filename)
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_AUDIO_EXT:
        return jsonify({'error': 'Only .mp3 files are allowed'}), 400

    media_dir = os.path.join(NOTES_DIR, 'media', slug)
    os.makedirs(media_dir, exist_ok=True)

    dest = os.path.join(media_dir, filename)
    # Avoid overwriting — append number if exists
    base, ext = os.path.splitext(filename)
    counter = 2
    while os.path.exists(dest):
        filename = f'{base}-{counter}{ext}'
        dest = os.path.join(media_dir, filename)
        counter += 1

    f.save(dest)
    return jsonify({'filename': filename}), 201


@app.route('/api/audio/<slug>/<filename>')
@login_required
def api_audio_serve(slug, filename):
    """Serve an MP3 file for playback."""
    media_dir = os.path.join(NOTES_DIR, 'media', slug)
    safe_name = secure_filename(filename)
    if not os.path.isfile(os.path.join(media_dir, safe_name)):
        return jsonify({'error': 'Audio not found'}), 404
    return send_from_directory(media_dir, safe_name, mimetype='audio/mpeg')


@app.route('/api/notes/<slug>/audio/<filename>', methods=['DELETE'])
@login_required
def api_audio_delete(slug, filename):
    """Delete a specific MP3 attached to a note."""
    media_dir = os.path.join(NOTES_DIR, 'media', slug)
    safe_name = secure_filename(filename)
    fpath = os.path.join(media_dir, safe_name)
    if os.path.isfile(fpath):
        os.remove(fpath)
        # Remove empty media dir
        if os.path.isdir(media_dir) and not os.listdir(media_dir):
            os.rmdir(media_dir)
        return jsonify({'ok': True})
    return jsonify({'error': 'File not found'}), 404


@app.route('/api/notes/<slug>/audio')
@login_required
def api_audio_list(slug):
    """List all MP3s attached to a note."""
    media_dir = os.path.join(NOTES_DIR, 'media', slug)
    files = []
    if os.path.isdir(media_dir):
        for fname in sorted(os.listdir(media_dir)):
            if fname.lower().endswith('.mp3'):
                fpath = os.path.join(media_dir, fname)
                files.append({
                    'filename': fname,
                    'size': os.path.getsize(fpath),
                })
    return jsonify(files)


# --- Image API ---

ALLOWED_IMAGE_EXT = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}


@app.route('/api/images/<filename>')
@login_required
def api_image_serve(filename):
    """Serve an image file from the shared images directory."""
    images_dir = os.path.join(NOTES_DIR, 'images')
    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify({'error': 'Invalid filename'}), 400
    ext = os.path.splitext(safe_name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXT:
        return jsonify({'error': 'Invalid image type'}), 400
    fpath = os.path.join(images_dir, safe_name)
    if not os.path.isfile(fpath):
        return jsonify({'error': 'Image not found'}), 404
    mime_map = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                '.gif': 'image/gif', '.webp': 'image/webp'}
    return send_from_directory(images_dir, safe_name, mimetype=mime_map.get(ext, 'image/png'))


# --- Startup ---

def sync_repo_notes():
    """Copy notes from the repo into NOTES_DIR if they don't already exist there.
    This handles the case where NOTES_DIR is a persistent disk (e.g. on Render)
    and the repo contains notes that haven't been copied over yet."""
    repo_notes = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notes')
    if repo_notes == NOTES_DIR:
        return  # Same directory, nothing to sync
    if not os.path.isdir(repo_notes):
        return

    copied = 0
    # Copy .md files
    for f in os.listdir(repo_notes):
        if f.endswith('.md'):
            src = os.path.join(repo_notes, f)
            dst = os.path.join(NOTES_DIR, f)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                copied += 1

    # Copy images directory
    repo_images = os.path.join(repo_notes, 'images')
    dest_images = os.path.join(NOTES_DIR, 'images')
    if os.path.isdir(repo_images):
        os.makedirs(dest_images, exist_ok=True)
        for f in os.listdir(repo_images):
            src = os.path.join(repo_images, f)
            dst = os.path.join(dest_images, f)
            if os.path.isfile(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)

    if copied > 0:
        print(f'[sync] Copied {copied} notes from repo to {NOTES_DIR}')
        rebuild_index()


sync_repo_notes()
load_index()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
