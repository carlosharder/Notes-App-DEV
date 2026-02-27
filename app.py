import io
import os
import re
import shutil
import zipfile
from datetime import datetime
from markupsafe import escape as html_escape
from flask import (
    Flask, render_template, request, redirect, url_for, flash, jsonify,
    send_from_directory, send_file,
)
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user,
)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB upload limit

# Database config
database_url = os.environ.get('DATABASE_URL', 'sqlite:///notes.sqlite')
# Render provides postgres:// but SQLAlchemy requires postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Media directory (images + audio only; notes are in the database)
MEDIA_DIR = os.environ.get(
    'MEDIA_DIR',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media'),
)
os.makedirs(MEDIA_DIR, exist_ok=True)

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# --- Models ---

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    notes = db.relationship('Note', backref='owner', lazy='dynamic',
                            cascade='all, delete-orphan')


class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    body = db.Column(db.Text, nullable=False, default='')
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    modified = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'slug', name='uq_user_slug'),
        db.Index('ix_notes_user_modified', 'user_id', 'modified'),
    )


class NoteShare(db.Model):
    __tablename__ = 'note_shares'

    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id', ondelete='CASCADE'), nullable=False)
    shared_with_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    permission = db.Column(db.String(10), nullable=False, default='edit')  # 'view' or 'edit'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    note = db.relationship('Note', backref=db.backref('shares', lazy='dynamic', cascade='all, delete-orphan'))
    shared_with = db.relationship('User', foreign_keys=[shared_with_id])

    __table_args__ = (
        db.UniqueConstraint('note_id', 'shared_with_id', name='uq_note_share'),
    )


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None


# --- Helpers ---

def slugify(title):
    slug = title.lower().strip()
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug or 'untitled'


def unique_slug(title, user_id, exclude_slug=None):
    base = slugify(title)
    existing = {
        n.slug for n in
        Note.query.filter_by(user_id=user_id).with_entities(Note.slug).all()
    }
    if exclude_slug:
        existing.discard(exclude_slug)
    if base not in existing:
        return base
    n = 2
    while f'{base}-{n}' in existing:
        n += 1
    return f'{base}-{n}'


def preview_text(body, length=120):
    text = re.sub(r'[#*`>\[\]!_~\-]', '', body)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > length:
        return text[:length] + '...'
    return text


def format_date(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str) if isinstance(iso_str, str) else iso_str
        return dt.strftime('%b %d, %Y %H:%M')
    except (ValueError, TypeError):
        return str(iso_str)


def short_date(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str) if isinstance(iso_str, str) else iso_str
        now = datetime.now()
        if dt.date() == now.date():
            return dt.strftime('%I:%M %p').lstrip('0')
        elif dt.year == now.year:
            return dt.strftime('%b %d')
        else:
            return dt.strftime('%m/%d/%y')
    except (ValueError, TypeError):
        return str(iso_str)


app.jinja_env.filters['format_date'] = format_date
app.jinja_env.filters['short_date'] = short_date
app.jinja_env.filters['preview'] = preview_text


def user_media_path(user_id, *parts):
    """Build a path under MEDIA_DIR/{user_id}/..."""
    return os.path.join(MEDIA_DIR, str(user_id), *parts)


# --- Plain-Text Rendering ---

def render_note(text, slug=None, user_id=None):
    if user_id:
        notes = Note.query.filter_by(user_id=user_id).with_entities(Note.title, Note.slug).all()
        title_map = {n.title.lower(): n.slug for n in notes}
    else:
        title_map = {}

    def resolve_hyperlinks(line_html):
        def replace_hyperlink(match):
            text = match.group(1)
            url = match.group(2)
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
        line_html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line_html)
        line_html = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', line_html)
        line_html = re.sub(r'__(.+?)__', r'<u>\1</u>', line_html)
        line_html = re.sub(r'~~(.+?)~~', r'<s>\1</s>', line_html)
        return line_html

    def resolve_inline(line_html):
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
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('app_shell'))
        flash('Invalid username or password.')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('app_shell'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:
            errors.append('Valid email required.')
        if not password or len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if User.query.filter_by(username=username).first():
            errors.append('Username already taken.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')

        if errors:
            for e in errors:
                flash(e)
        else:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
            )
            db.session.add(user)
            db.session.commit()
            # Create media directories for the new user
            os.makedirs(user_media_path(user.id, 'images'), exist_ok=True)
            os.makedirs(user_media_path(user.id, 'audio'), exist_ok=True)
            login_user(user)
            return redirect(url_for('app_shell'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# --- Main App Routes ---

@app.route('/healthz')
def healthz():
    return 'ok', 200


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
    q = request.args.get('q', '').strip()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 50))

    query = Note.query.filter_by(user_id=current_user.id)

    if q:
        pattern = f'%{q}%'
        query = query.filter(
            db.or_(
                Note.title.ilike(pattern),
                Note.body.ilike(pattern),
            )
        )

    query = query.order_by(Note.modified.desc())
    total = query.count()
    notes = query.offset((page - 1) * limit).limit(limit).all()

    return jsonify({
        'notes': [{
            'slug': n.slug,
            'title': n.title,
            'modified': n.modified.isoformat(timespec='seconds'),
            'created': n.created.isoformat(timespec='seconds'),
            'preview': preview_text(n.body),
        } for n in notes],
        'total': total,
        'page': page,
    })


@app.route('/api/notes/<slug>')
@login_required
def api_note_get(slug):
    note, permission = get_note_with_access(slug, current_user.id)
    if not note:
        return jsonify({'error': 'not found'}), 404
    html = render_note(note.body, slug, note.user_id)
    owner = User.query.get(note.user_id)
    return jsonify({
        'slug': note.slug,
        'title': note.title,
        'body': note.body,
        'html': html,
        'created': note.created.isoformat(timespec='seconds'),
        'modified': note.modified.isoformat(timespec='seconds'),
        'permission': permission,
        'owner': owner.username if owner else None,
        'is_own': note.user_id == current_user.id,
    })


@app.route('/api/notes', methods=['POST'])
@login_required
def api_note_create():
    data = request.get_json()
    title = (data.get('title') or '').strip() or 'Untitled'
    body = data.get('body', '')
    slug = unique_slug(title, current_user.id)
    now = datetime.utcnow()

    note = Note(user_id=current_user.id, slug=slug, title=title,
                body=body, created=now, modified=now)
    db.session.add(note)
    db.session.commit()

    return jsonify({'slug': slug, 'title': title}), 201


@app.route('/api/notes/<slug>', methods=['PUT'])
@login_required
def api_note_update(slug):
    note, permission = get_note_with_access(slug, current_user.id)
    if not note:
        return jsonify({'error': 'not found'}), 404
    if permission == 'view':
        return jsonify({'error': 'read-only access'}), 403

    data = request.get_json()
    title = (data.get('title') or '').strip() or note.title
    body = data.get('body', note.body)

    new_slug = unique_slug(title, note.user_id, exclude_slug=slug)
    if new_slug != slug:
        # Rename audio directory if it exists
        old_media = user_media_path(note.user_id, 'audio', slug)
        new_media = user_media_path(note.user_id, 'audio', new_slug)
        if os.path.isdir(old_media):
            os.makedirs(os.path.dirname(new_media), exist_ok=True)
            os.rename(old_media, new_media)

    note.slug = new_slug
    note.title = title
    note.body = body
    note.modified = datetime.utcnow()
    db.session.commit()

    return jsonify({'slug': new_slug, 'title': title})


@app.route('/api/notes/<slug>', methods=['DELETE'])
@login_required
def api_note_delete(slug):
    note = Note.query.filter_by(user_id=current_user.id, slug=slug).first()
    if note:
        db.session.delete(note)
        db.session.commit()
    # Delete attached audio
    media_dir = user_media_path(current_user.id, 'audio', slug)
    if os.path.isdir(media_dir):
        shutil.rmtree(media_dir)
    return jsonify({'ok': True})


@app.route('/api/notes/<slug>/toggle', methods=['POST'])
@login_required
def api_toggle_checkbox(slug):
    note, permission = get_note_with_access(slug, current_user.id)
    if not note:
        return jsonify({'error': 'not found'}), 404
    if permission == 'view':
        return jsonify({'error': 'read-only access'}), 403

    data = request.get_json()
    line_num = data.get('line')
    checked = data.get('checked')

    lines = note.body.split('\n')
    if 0 <= line_num < len(lines):
        if checked:
            lines[line_num] = re.sub(r'\[ \]', '[x]', lines[line_num], count=1)
        else:
            lines[line_num] = re.sub(r'\[x\]', '[ ]', lines[line_num], count=1)

    note.body = '\n'.join(lines)
    note.modified = datetime.utcnow()
    db.session.commit()

    return jsonify({'ok': True})


@app.route('/api/notes/titles')
@login_required
def api_note_titles():
    notes = Note.query.filter_by(user_id=current_user.id)\
        .with_entities(Note.title, Note.slug)\
        .order_by(Note.title).all()
    return jsonify([{'title': n.title, 'slug': n.slug} for n in notes])


# --- Audio API ---

ALLOWED_AUDIO_EXT = {'.mp3'}


@app.route('/api/notes/<slug>/audio', methods=['POST'])
@login_required
def api_audio_upload(slug):
    """Upload an MP3 file attached to a note."""
    note = Note.query.filter_by(user_id=current_user.id, slug=slug).first()
    if not note:
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

    media_dir = user_media_path(current_user.id, 'audio', slug)
    os.makedirs(media_dir, exist_ok=True)

    dest = os.path.join(media_dir, filename)
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
    note, permission = get_note_with_access(slug, current_user.id)
    if not note:
        return jsonify({'error': 'Audio not found'}), 404
    media_dir = user_media_path(note.user_id, 'audio', slug)
    safe_name = secure_filename(filename)
    if not os.path.isfile(os.path.join(media_dir, safe_name)):
        return jsonify({'error': 'Audio not found'}), 404
    return send_from_directory(media_dir, safe_name, mimetype='audio/mpeg')


@app.route('/api/notes/<slug>/audio/<filename>', methods=['DELETE'])
@login_required
def api_audio_delete(slug, filename):
    """Delete a specific MP3 attached to a note."""
    media_dir = user_media_path(current_user.id, 'audio', slug)
    safe_name = secure_filename(filename)
    fpath = os.path.join(media_dir, safe_name)
    if os.path.isfile(fpath):
        os.remove(fpath)
        if os.path.isdir(media_dir) and not os.listdir(media_dir):
            os.rmdir(media_dir)
        return jsonify({'ok': True})
    return jsonify({'error': 'File not found'}), 404


@app.route('/api/notes/<slug>/audio')
@login_required
def api_audio_list(slug):
    """List all MP3s attached to a note."""
    media_dir = user_media_path(current_user.id, 'audio', slug)
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
@app.route('/api/images/<int:owner_id>/<filename>')
@login_required
def api_image_serve(filename, owner_id=None):
    """Serve an image file from the user's images directory."""
    images_dir = user_media_path(owner_id or current_user.id, 'images')
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


# --- Helper: access check for shared notes ---

def get_note_with_access(slug, user_id):
    """Return (note, permission) if user owns or has shared access, else (None, None)."""
    note = Note.query.filter_by(user_id=user_id, slug=slug).first()
    if note:
        return note, 'owner'
    # Check shared notes: find note by slug where shared with this user
    share = (
        db.session.query(NoteShare, Note)
        .join(Note, NoteShare.note_id == Note.id)
        .filter(NoteShare.shared_with_id == user_id, Note.slug == slug)
        .first()
    )
    if share:
        return share.Note, share.NoteShare.permission
    return None, None


# --- ZIP Download ---

@app.route('/api/notes/download')
@login_required
def api_notes_download():
    """Download all user's notes as a ZIP file."""
    notes = Note.query.filter_by(user_id=current_user.id)\
        .order_by(Note.modified.desc()).all()

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for note in notes:
            filename = note.slug + '.txt'
            content = note.title + '\n' + ('=' * len(note.title)) + '\n\n' + note.body
            zf.writestr(filename, content)

    buf.seek(0)
    return send_file(
        buf,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'notes-{current_user.username}.zip',
    )


# --- Share API ---

@app.route('/api/notes/<slug>/share', methods=['POST'])
@login_required
def api_note_share(slug):
    """Share a note with another user by username."""
    note = Note.query.filter_by(user_id=current_user.id, slug=slug).first()
    if not note:
        return jsonify({'error': 'Note not found'}), 404

    data = request.get_json()
    username = (data.get('username') or '').strip()
    permission = data.get('permission', 'edit')

    if permission not in ('view', 'edit'):
        return jsonify({'error': 'Permission must be "view" or "edit"'}), 400

    if not username:
        return jsonify({'error': 'Username required'}), 400

    target_user = User.query.filter_by(username=username).first()
    if not target_user:
        return jsonify({'error': 'User not found'}), 404

    if target_user.id == current_user.id:
        return jsonify({'error': 'Cannot share with yourself'}), 400

    existing = NoteShare.query.filter_by(
        note_id=note.id, shared_with_id=target_user.id
    ).first()
    if existing:
        existing.permission = permission
        db.session.commit()
        return jsonify({'ok': True, 'message': 'Permission updated'})

    share = NoteShare(
        note_id=note.id,
        shared_with_id=target_user.id,
        permission=permission,
    )
    db.session.add(share)
    db.session.commit()
    return jsonify({'ok': True, 'message': f'Shared with {username}'}), 201


@app.route('/api/notes/<slug>/share/<int:share_id>', methods=['DELETE'])
@login_required
def api_note_unshare(slug, share_id):
    """Remove a collaborator from a note."""
    note = Note.query.filter_by(user_id=current_user.id, slug=slug).first()
    if not note:
        return jsonify({'error': 'Note not found'}), 404

    share = NoteShare.query.filter_by(id=share_id, note_id=note.id).first()
    if share:
        db.session.delete(share)
        db.session.commit()
    return jsonify({'ok': True})


@app.route('/api/notes/<slug>/collaborators')
@login_required
def api_note_collaborators(slug):
    """List collaborators for a note."""
    note = Note.query.filter_by(user_id=current_user.id, slug=slug).first()
    if not note:
        return jsonify({'error': 'Note not found'}), 404

    shares = NoteShare.query.filter_by(note_id=note.id).all()
    return jsonify([{
        'id': s.id,
        'username': s.shared_with.username,
        'permission': s.permission,
    } for s in shares])


@app.route('/api/shared')
@login_required
def api_shared_notes():
    """List notes shared with current user."""
    shares = (
        db.session.query(NoteShare, Note, User)
        .join(Note, NoteShare.note_id == Note.id)
        .join(User, Note.user_id == User.id)
        .filter(NoteShare.shared_with_id == current_user.id)
        .order_by(Note.modified.desc())
        .all()
    )
    return jsonify([{
        'slug': note.slug,
        'title': note.title,
        'modified': note.modified.isoformat(timespec='seconds'),
        'created': note.created.isoformat(timespec='seconds'),
        'preview': preview_text(note.body),
        'owner': owner.username,
        'permission': share.permission,
        'shared': True,
    } for share, note, owner in shares])


# --- Startup ---

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
