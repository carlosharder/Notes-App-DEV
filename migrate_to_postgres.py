#!/usr/bin/env python3
"""
One-time migration: .md files -> PostgreSQL (or SQLite) rows.

Usage:
    # Local (SQLite):
    python migrate_to_postgres.py

    # Production (Postgres):
    DATABASE_URL=postgresql://... python migrate_to_postgres.py

Requires the same environment variables as app.py.
"""
import os
import re
import glob
import shutil
from datetime import datetime

from app import app, db, User, Note, MEDIA_DIR

NOTES_DIR = os.environ.get('NOTES_DIR', './notes')
ORIGINAL_USERNAME = os.environ.get('APP_USERNAME', 'carlosharder')
ORIGINAL_EMAIL = os.environ.get('ORIGINAL_EMAIL', 'carlos@example.com')
ORIGINAL_PASSWORD_HASH = os.environ.get(
    'PASSWORD_HASH',
    'pbkdf2:sha256:1000000$oz91NOa38dzvn3pz$d2fe5614d8d37ceb1bafd2cc7f016f98602cb02def61201464f05bd288b226cc',
)


def parse_note(filepath):
    """Parse a .md file with YAML-like frontmatter (line-based to handle edge cases)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    slug = os.path.splitext(os.path.basename(filepath))[0]
    title = slug
    created = modified = datetime.now()

    # Parse frontmatter line by line: find opening --- and closing ---
    body_start = 0
    if lines and lines[0].strip() == '---':
        front_lines = []
        closed = False
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                # Only treat as closing delimiter if it's on its own line
                # and we've seen at least one frontmatter key
                closed = True
                body_start = i + 1
                break
            front_lines.append(lines[i])

        if closed:
            for line in front_lines:
                if ':' in line:
                    key, val = line.split(':', 1)
                    key, val = key.strip(), val.strip()
                    if key == 'title' and val and val != '---':
                        title = val
                    elif key == 'created':
                        try:
                            created = datetime.fromisoformat(val)
                        except ValueError:
                            pass
                    elif key == 'modified':
                        try:
                            modified = datetime.fromisoformat(val)
                        except ValueError:
                            pass

    body = ''.join(lines[body_start:]).strip()
    return slug, title, body, created, modified


def migrate():
    with app.app_context():
        db.create_all()

        # Step 1: Create or find the original user
        user = User.query.filter_by(username=ORIGINAL_USERNAME).first()
        if not user:
            user = User(
                username=ORIGINAL_USERNAME,
                email=ORIGINAL_EMAIL,
                password_hash=ORIGINAL_PASSWORD_HASH,
            )
            db.session.add(user)
            db.session.commit()
            print(f'Created user: {ORIGINAL_USERNAME} (id={user.id})')
        else:
            print(f'Found existing user: {ORIGINAL_USERNAME} (id={user.id})')

        # Step 2: Migrate note files to DB rows
        md_files = glob.glob(os.path.join(NOTES_DIR, '*.md'))
        print(f'Found {len(md_files)} .md files')

        migrated = 0
        skipped = 0
        for filepath in md_files:
            slug, title, body, created, modified = parse_note(filepath)
            existing = Note.query.filter_by(user_id=user.id, slug=slug).first()
            if existing:
                skipped += 1
                continue
            note = Note(
                user_id=user.id, slug=slug, title=title,
                body=body, created=created, modified=modified,
            )
            db.session.add(note)
            migrated += 1
            if migrated % 100 == 0:
                db.session.commit()
                print(f'  ...migrated {migrated}')

        db.session.commit()
        print(f'Migrated {migrated} notes ({skipped} skipped as duplicates)')

        # Step 3: Move media files to per-user structure
        user_images = os.path.join(MEDIA_DIR, str(user.id), 'images')
        user_audio = os.path.join(MEDIA_DIR, str(user.id), 'audio')
        os.makedirs(user_images, exist_ok=True)
        os.makedirs(user_audio, exist_ok=True)

        # Copy images
        old_images = os.path.join(NOTES_DIR, 'images')
        if os.path.isdir(old_images):
            count = 0
            for fname in os.listdir(old_images):
                src = os.path.join(old_images, fname)
                dst = os.path.join(user_images, fname)
                if os.path.isfile(src) and not os.path.exists(dst):
                    shutil.copy2(src, dst)
                    count += 1
            print(f'Copied {count} images to {user_images}')
        else:
            print('No images directory found, skipping.')

        # Copy audio directories
        old_media = os.path.join(NOTES_DIR, 'media')
        if os.path.isdir(old_media):
            count = 0
            for slug_dir in os.listdir(old_media):
                src_dir = os.path.join(old_media, slug_dir)
                dst_dir = os.path.join(user_audio, slug_dir)
                if os.path.isdir(src_dir):
                    shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
                    count += 1
            print(f'Copied {count} audio directories to {user_audio}')
        else:
            print('No media directory found, skipping.')

        print('Migration complete!')


if __name__ == '__main__':
    migrate()
