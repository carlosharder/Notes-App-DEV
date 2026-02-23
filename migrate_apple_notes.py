#!/usr/bin/env python3
"""
Migration script: Import Apple Notes .md exports into the Roam Notes app.

What it does:
1. Reads each .md file from the Apple Notes export folder
2. Extracts the title from the first `# Title` line
3. Slugifies the title for the filename
4. Uses file system dates for created/modified
5. Strips the `# Title` heading (title goes in frontmatter)
6. Copies referenced images to notes/images/ (shared across all notes)
7. Copies referenced MP3 audio to notes/media/<slug>/ (per-note)
8. Writes the new .md with YAML frontmatter to the notes directory
"""

import os
import re
import shutil
from datetime import datetime


# --- Configuration ---
SOURCE_DIR = os.path.expanduser('~/Desktop/Notes')
TARGET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notes')
SOURCE_IMAGES = os.path.join(SOURCE_DIR, 'images')
SOURCE_ATTACHMENTS = os.path.join(SOURCE_DIR, 'attachments')
TARGET_IMAGES = os.path.join(TARGET_DIR, 'images')

# --- Helpers ---

def slugify(title):
    """Convert a title to a URL-safe slug."""
    slug = title.lower().strip()
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug or 'untitled'


def unique_slug(title, existing_slugs):
    """Generate a unique slug, appending -2, -3, etc. if needed."""
    base = slugify(title)
    if not base:
        base = 'untitled'
    if base not in existing_slugs:
        existing_slugs.add(base)
        return base
    n = 2
    while f'{base}-{n}' in existing_slugs:
        n += 1
    slug = f'{base}-{n}'
    existing_slugs.add(slug)
    return slug


def get_file_dates(filepath):
    """Get created and modified dates from file metadata."""
    stat = os.stat(filepath)
    # On macOS, st_birthtime is the creation time
    try:
        created = datetime.fromtimestamp(stat.st_birthtime)
    except AttributeError:
        created = datetime.fromtimestamp(stat.st_ctime)
    modified = datetime.fromtimestamp(stat.st_mtime)
    return created.isoformat(timespec='seconds'), modified.isoformat(timespec='seconds')


def extract_title_and_body(content):
    """Extract the title from the first # heading and return (title, body)."""
    lines = content.split('\n')
    title = None
    body_start = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        # First non-empty line — check if it's a heading
        match = re.match(r'^#\s+(.+)', stripped)
        if match:
            title = match.group(1).strip()
            body_start = i + 1
            # Skip blank lines after the title
            while body_start < len(lines) and not lines[body_start].strip():
                body_start += 1
        break

    if title is None:
        # No heading found — use first non-empty line or 'Untitled'
        for line in lines:
            if line.strip():
                title = line.strip()[:80]
                break
        if title is None:
            title = 'Untitled'
        body_start = 0

    body = '\n'.join(lines[body_start:]).rstrip()
    return title, body


def find_referenced_images(body):
    """Find all image references like ![alt](images/UUID.ext)."""
    return re.findall(r'!\[[^\]]*\]\((images/[^)]+)\)', body)


def find_referenced_audio(body):
    """Find all attachment references like [name](attachments/UUID.mp3)."""
    matches = re.findall(r'\[([^\]]*)\]\((attachments/([^)]+\.mp3))\)', body, re.IGNORECASE)
    return matches  # list of (alt_text, full_path, filename)


def convert_image_refs_for_app(body):
    """
    Convert ![alt](images/UUID.ext) to a format the app can serve.
    Images will be served from /api/images/<filename>.
    """
    def replace_img(match):
        alt = match.group(1)
        img_path = match.group(2)
        filename = os.path.basename(img_path)
        # Keep the markdown image syntax — the app's render_note will handle it
        return f'![{alt}](images/{filename})'
    return re.sub(r'!\[([^\]]*)\]\((images/[^)]+)\)', replace_img, body)


def convert_audio_refs_for_app(body, slug):
    """
    Convert [name](attachments/UUID.mp3) to [audio:filename.mp3] format
    that the app's render_note understands.
    """
    def replace_audio(match):
        filename = match.group(2)
        return f'[audio:{filename}]'
    return re.sub(r'\[([^\]]*)\]\(attachments/([^)]+\.mp3)\)', replace_audio, body, flags=re.IGNORECASE)


def clean_html_artifacts(body):
    """Remove leftover HTML tags from Apple Notes export."""
    # Remove <span> tags with styles
    body = re.sub(r'<span[^>]*>', '', body)
    body = re.sub(r'</span>', '', body)
    # Remove <u> tags (underline)
    body = re.sub(r'<u>(.*?)</u>', r'\1', body)
    # Remove empty HTML comments
    body = re.sub(r'<!--.*?-->', '', body)
    return body


# --- Main Migration ---

def migrate():
    os.makedirs(TARGET_DIR, exist_ok=True)
    os.makedirs(TARGET_IMAGES, exist_ok=True)

    # Collect existing slugs from the target directory
    existing_slugs = set()
    for f in os.listdir(TARGET_DIR):
        if f.endswith('.md'):
            existing_slugs.add(os.path.splitext(f)[0])

    source_files = sorted([
        f for f in os.listdir(SOURCE_DIR)
        if f.endswith('.md')
    ])

    print(f"Found {len(source_files)} .md files to migrate")
    print(f"Target directory: {TARGET_DIR}")
    print()

    migrated = 0
    skipped = 0
    images_copied = 0
    audio_copied = 0
    errors = []

    for filename in source_files:
        source_path = os.path.join(SOURCE_DIR, filename)
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title and body
            title, body = extract_title_and_body(content)

            # Get file dates
            created, modified = get_file_dates(source_path)

            # Generate unique slug
            slug = unique_slug(title, existing_slugs)

            # Clean up body
            body = clean_html_artifacts(body)

            # Handle images — copy referenced images to target
            image_refs = find_referenced_images(body)
            for img_path in image_refs:
                img_filename = os.path.basename(img_path)
                src_img = os.path.join(SOURCE_DIR, img_path)
                dst_img = os.path.join(TARGET_IMAGES, img_filename)
                if os.path.isfile(src_img) and not os.path.exists(dst_img):
                    shutil.copy2(src_img, dst_img)
                    images_copied += 1

            # Update image references in body
            body = convert_image_refs_for_app(body)

            # Handle audio — copy MP3s to media/<slug>/
            audio_refs = find_referenced_audio(body)
            if audio_refs:
                media_dir = os.path.join(TARGET_DIR, 'media', slug)
                os.makedirs(media_dir, exist_ok=True)
                for alt_text, full_path, audio_filename in audio_refs:
                    src_audio = os.path.join(SOURCE_DIR, full_path)
                    dst_audio = os.path.join(media_dir, audio_filename)
                    if os.path.isfile(src_audio) and not os.path.exists(dst_audio):
                        shutil.copy2(src_audio, dst_audio)
                        audio_copied += 1

            # Convert audio references to app format
            body = convert_audio_refs_for_app(body, slug)

            # Write the note with frontmatter
            target_path = os.path.join(TARGET_DIR, f'{slug}.md')
            frontmatter = f'---\ntitle: {title}\ncreated: {created}\nmodified: {modified}\n---\n\n'
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter + body)

            migrated += 1
            if migrated % 50 == 0:
                print(f"  ...migrated {migrated}/{len(source_files)}")

        except Exception as e:
            errors.append((filename, str(e)))
            skipped += 1

    print()
    print(f"=== Migration Complete ===")
    print(f"  Notes migrated: {migrated}")
    print(f"  Notes skipped:  {skipped}")
    print(f"  Images copied:  {images_copied}")
    print(f"  Audio copied:   {audio_copied}")

    if errors:
        print(f"\n  Errors:")
        for fname, err in errors:
            print(f"    {fname}: {err}")

    # Delete stale index so the app rebuilds it on next start
    index_path = os.path.join(TARGET_DIR, '.notes_index.json')
    if os.path.exists(index_path):
        os.remove(index_path)
        print(f"\n  Deleted stale index ({index_path}) — app will rebuild on start.")

    print(f"\n  Done! Restart the Flask app to load all notes.")


if __name__ == '__main__':
    migrate()
