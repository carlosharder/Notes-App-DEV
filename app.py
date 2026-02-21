import os
import re
import glob
import markdown
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__)
NOTES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notes')
os.makedirs(NOTES_DIR, exist_ok=True)


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
    existing = {
        os.path.splitext(os.path.basename(f))[0]
        for f in glob.glob(os.path.join(NOTES_DIR, '*.md'))
    }
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


def render_md(text):
    return markdown.markdown(
        text, extensions=['fenced_code', 'tables', 'nl2br', 'sane_lists']
    )


def get_all_notes():
    files = glob.glob(os.path.join(NOTES_DIR, '*.md'))
    notes = [parse_note(f) for f in files]
    notes.sort(key=lambda n: n['modified'], reverse=True)
    return notes


def format_date(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime('%b %d, %Y %H:%M')
    except (ValueError, TypeError):
        return iso_str


def preview_text(body, length=150):
    text = re.sub(r'[#*`>\[\]!_~\-]', '', body)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > length:
        return text[:length] + '...'
    return text


app.jinja_env.filters['format_date'] = format_date
app.jinja_env.filters['preview'] = preview_text


# --- Routes ---

@app.route('/')
def home():
    return redirect(url_for('note_list'))


@app.route('/notes')
def note_list():
    query = request.args.get('q', '').strip()
    notes = get_all_notes()
    if query:
        q = query.lower()
        notes = [
            n for n in notes
            if q in n['title'].lower() or q in n['body'].lower()
        ]
    return render_template('index.html', notes=notes, query=query)


@app.route('/notes/new')
def note_new():
    return render_template('editor.html', mode='new', title='', body='')


@app.route('/notes', methods=['POST'])
def note_create():
    title = request.form.get('title', '').strip() or 'Untitled'
    body = request.form.get('body', '')
    slug = unique_slug(title)
    now = datetime.now().isoformat(timespec='seconds')
    write_note(slug, title, body, now, now)
    return redirect(url_for('note_view', slug=slug))


@app.route('/notes/<slug>')
def note_view(slug):
    filepath = os.path.join(NOTES_DIR, f'{slug}.md')
    if not os.path.isfile(filepath):
        abort(404)
    note = parse_note(filepath)
    content = render_md(note['body'])
    return render_template('view.html', note=note, content=content)


@app.route('/notes/<slug>/edit')
def note_edit(slug):
    filepath = os.path.join(NOTES_DIR, f'{slug}.md')
    if not os.path.isfile(filepath):
        abort(404)
    note = parse_note(filepath)
    return render_template(
        'editor.html', mode='edit', title=note['title'],
        body=note['body'], slug=slug
    )


@app.route('/notes/<slug>', methods=['POST'])
def note_update(slug):
    filepath = os.path.join(NOTES_DIR, f'{slug}.md')
    if not os.path.isfile(filepath):
        abort(404)
    note = parse_note(filepath)
    title = request.form.get('title', '').strip() or 'Untitled'
    body = request.form.get('body', '')
    new_slug = unique_slug(title, exclude_slug=slug)
    now = datetime.now().isoformat(timespec='seconds')
    if new_slug != slug:
        os.remove(filepath)
    write_note(new_slug, title, body, note['created'], now)
    return redirect(url_for('note_view', slug=new_slug))


@app.route('/notes/<slug>/delete', methods=['POST'])
def note_delete(slug):
    filepath = os.path.join(NOTES_DIR, f'{slug}.md')
    if os.path.isfile(filepath):
        os.remove(filepath)
    return redirect(url_for('note_list'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
