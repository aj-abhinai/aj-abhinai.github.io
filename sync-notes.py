import os
import re
import shutil
from pathlib import Path
from datetime import datetime

# Configuration
SOURCE_DIR = Path(r"D:\ajabhinai")
DEST_DIR = Path(__file__).parent / "temp-content" / "Notes"
ASSETS_DIR = DEST_DIR / "assets"
SKIP_DIRS = {"Archives"}  # Folders to skip in source
ASSET_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.pdf', '.mp4', '.mp3'}

# Ensure directories exist
DEST_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def has_publish_tag(content: str) -> bool:
    """Check if content contains #published tag."""
    return bool(re.search(r'#published\b', content, re.IGNORECASE))


def parse_frontmatter(content: str) -> tuple[str | None, str]:
    """Parse frontmatter and body from content."""
    if not content.startswith('---'):
        return None, content
    
    end_index = content.find('---', 3)
    if end_index == -1:
        return None, content
    
    frontmatter = content[4:end_index].strip()
    body = content[end_index + 3:].strip()
    return frontmatter, body


def generate_permalink(filename: str) -> str:
    """Generate permalink from filename."""
    name = Path(filename).stem
    permalink = name.lower().replace(' ', '-')
    permalink = re.sub(r'[^a-z0-9-]', '', permalink)
    permalink = re.sub(r'-+', '-', permalink).strip('-')
    return permalink  # No leading slash


def generate_new_frontmatter(filename: str) -> str:
    """Generate frontmatter for a new note."""
    title = Path(filename).stem
    permalink = generate_permalink(filename)
    date = datetime.now().strftime('%Y-%m-%d')
    
    return f"""title: "{title}"
permalink: {permalink}
date: {date}
publish: true"""


def normalize_frontmatter(frontmatter: str) -> str:
    """Normalize frontmatter to fix Obsidian-specific formats.
    - Convert checkbox publish values to text 'true'
    - Ensure publish field exists and is 'true'
    """
    # Fix publish field - handle checkboxes and various formats
    # Match publish: followed by any value (checkbox, true, false, etc.)
    if re.search(r'publish:', frontmatter, re.IGNORECASE):
        # Replace any publish value with 'true'
        frontmatter = re.sub(r'publish:\s*\S*', 'publish: true', frontmatter, flags=re.IGNORECASE)
    else:
        # Add publish: true if not present
        frontmatter = frontmatter.rstrip() + '\npublish: true'
    
    return frontmatter


def update_frontmatter_with_modified(frontmatter: str) -> str:
    """Update frontmatter with last-modified date."""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # First normalize the frontmatter
    frontmatter = normalize_frontmatter(frontmatter)
    
    # Check if last-modified already exists
    if 'last-modified:' in frontmatter:
        # Update existing last-modified
        frontmatter = re.sub(r'last-modified:\s*\S+', f'last-modified: {today}', frontmatter)
    else:
        # Add last-modified at the end
        frontmatter = frontmatter.rstrip() + f'\nlast-modified: {today}'
    
    return frontmatter


def get_published_note_names(files: list[Path]) -> set[str]:
    """Get set of filenames that have #published tag."""
    published = set()
    for file in files:
        try:
            content = file.read_text(encoding='utf-8')
            if has_publish_tag(content):
                published.add(file.stem)  # filename without extension
        except Exception:
            pass
    return published


def find_asset_in_source(asset_name: str, source_dir: Path, skip_dirs: set[str]) -> Path | None:
    """Find an asset file by name in the source directory."""
    for item in source_dir.rglob('*'):
        # Skip directories in skip list
        if any(skip in item.parts for skip in skip_dirs):
            continue
        if item.is_file() and item.name == asset_name:
            return item
    return None


def process_assets(content: str, source_file: Path, assets_copied: set[str]) -> tuple[str, int]:
    """Find and copy assets referenced in content, update paths."""
    copied_count = 0
    
    # Pattern for Obsidian-style embeds: ![[image.png]]
    def replace_obsidian_embed(match):
        nonlocal copied_count
        asset_name = match.group(1).strip()
        
        # Check if it's an actual asset file on disk
        asset_path = find_asset_in_source(asset_name, SOURCE_DIR, SKIP_DIRS)
        if asset_path and asset_path.suffix.lower() in ASSET_EXTENSIONS:
            dest_asset = ASSETS_DIR / asset_name
            if asset_name not in assets_copied:
                shutil.copy2(asset_path, dest_asset)
                assets_copied.add(asset_name)
                copied_count += 1
            # Update to relative path
            return f"![{asset_name}](./assets/{asset_name})"
        # Not an asset — leave it for process_embedded_notes
        return match.group(0)
    
    # Pattern for standard markdown: ![alt](path)
    def replace_md_image(match):
        nonlocal copied_count
        alt = match.group(1)
        path = match.group(2).strip()
        
        # Skip external URLs
        if path.startswith(('http://', 'https://', './')):
            return match.group(0)
        
        asset_name = Path(path).name
        asset_path = find_asset_in_source(asset_name, SOURCE_DIR, SKIP_DIRS)
        if asset_path and asset_path.suffix.lower() in ASSET_EXTENSIONS:
            dest_asset = ASSETS_DIR / asset_name
            if asset_name not in assets_copied:
                shutil.copy2(asset_path, dest_asset)
                assets_copied.add(asset_name)
                copied_count += 1
            return f"![{alt}](./assets/{asset_name})"
        return match.group(0)
    
    # Process Obsidian embeds ![[...]]
    content = re.sub(r'!\[\[([^\]]+)\]\]', replace_obsidian_embed, content)
    # Process standard markdown images ![...](...)
    content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_md_image, content)
    
    return content, copied_count


def process_embedded_notes(content: str, published_names: set[str]) -> str:
    published_lookup = {name.casefold(): name for name in published_names}

    def replace_embed(match):
        target = match.group(1).strip()
        note_name = target.split("#")[0].strip()
        if not note_name:
            return match.group(0)
        if note_name.casefold() not in published_lookup:
            return ""
        canonical = published_lookup[note_name.casefold()]
        suffix = target[len(note_name):]
        return f"[[{canonical}{suffix}]]"

    return re.sub(r'!\[\[([^\]]+)\]\]', replace_embed, content)


def process_backlinks(content: str, published_names: set[str], current_note: str) -> str:
    """Keep same-note links, keep links to published notes, otherwise show as text.

    Also normalizes links to match the flattened destination structure by stripping
    folders and .md extensions when rebuilding published links.
    """
    published_lookup = {name.casefold(): name for name in published_names}
    current_lookup = current_note.casefold()

    def is_published(note_name: str) -> bool:
        return note_name.casefold() in published_lookup

    def is_same_note(note_name: str) -> bool:
        return note_name.casefold() == current_lookup

    def normalize_note_name(raw: str) -> str:
        # Strip folders and .md extension
        name = raw.replace("\\", "/").split("/")[-1].strip()
        if name.lower().endswith(".md"):
            name = name[:-3]
        return name

    def canonical_note_name(note_name: str) -> str:
        return published_lookup.get(note_name.casefold(), note_name)

    # Process Obsidian-style wikilinks [[...]] (but not embeds ![[...]])
    def replace_wikilink(match):
        inner = match.group(1).strip()
        if not inner:
            return match.group(0)

        if "|" in inner:
            target_part, alias = inner.split("|", 1)
            target_part = target_part.strip()
            alias = alias.strip()
        else:
            target_part = inner
            alias = None

        # Same-note anchors like [[#Heading]] or [[#^blockid]] should stay as links
        if target_part.startswith(("#", "^")):
            return match.group(0)

        # Split off heading/block reference if present
        note_part = target_part
        anchor = ""
        if "#" in target_part:
            note_part, anchor_tail = target_part.split("#", 1)
            anchor = f"#{anchor_tail}"
        elif "^" in target_part:
            note_part, anchor_tail = target_part.split("^", 1)
            anchor = f"^{anchor_tail}"

        note_part = note_part.strip()
        if not note_part:
            return match.group(0)

        note_name = normalize_note_name(note_part)
        if not note_name:
            return match.group(0)

        if is_same_note(note_name):
            return match.group(0)

        if not is_published(note_name):
            # Non-published target: convert to plain text
            if alias:
                return alias
            return f"{note_name}{anchor}"

        # Published target: rematch to flattened structure
        note_display = canonical_note_name(note_name)
        alias_part = f"|{alias}" if alias else ""
        return f"[[{note_display}{anchor}{alias_part}]]"

    content = re.sub(r'(?<!\!)\[\[([^\]]+)\]\]', replace_wikilink, content)

    def split_md_destination(raw: str) -> tuple[str, str, bool]:
        raw = raw.strip()
        if raw.startswith("<"):
            end = raw.find(">")
            if end != -1:
                dest = raw[1:end]
                rest = raw[end + 1:].strip()
                title = f" {rest}" if rest else ""
                return dest, title, True
            return raw, "", False

        # Detect title at the end (CommonMark-style "title" or 'title' or (title))
        title_match = re.search(r'\s+("([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\'|\([^()]*\))\s*$', raw)
        if title_match:
            dest = raw[:title_match.start()].strip()
            title = " " + title_match.group(1).strip()
            return dest, title, False

        return raw, "", False

    def replace_md_link(text: str, target_raw: str, original: str) -> str:
        url, title, used_angle = split_md_destination(target_raw)

        # External links or same-note anchors should stay as links
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', url):
            return original
        if url.startswith("#"):
            return original

        base, _, fragment = url.partition("#")
        base = base.lstrip("./").strip()
        if not base:
            return original

        ext = Path(base).suffix.lower()
        # Only treat .md or extensionless links as notes
        if ext and ext != ".md":
            return original

        note_name = normalize_note_name(base)
        if not note_name:
            return original

        if is_same_note(note_name):
            return original

        if not is_published(note_name):
            return text

        note_display = canonical_note_name(note_name)
        new_url = note_display
        if ext == ".md":
            new_url += ".md"
        if fragment:
            new_url += f"#{fragment}"
        if used_angle:
            new_url = f"<{new_url}>"

        return f"[{text}]({new_url}{title})"

    def replace_markdown_links(content_in: str) -> str:
        result = []
        i = 0
        length = len(content_in)
        while i < length:
            if content_in[i] == "[" and (i == 0 or content_in[i - 1] != "!"):
                # Find closing ]
                j = i + 1
                while j < length and content_in[j] != "]":
                    j += 1
                if j < length and j + 1 < length and content_in[j + 1] == "(":
                    # Parse destination with balanced parentheses
                    k = j + 2
                    depth = 1
                    while k < length and depth > 0:
                        if content_in[k] == "\\":
                            k += 2
                            continue
                        if content_in[k] == "(":
                            depth += 1
                        elif content_in[k] == ")":
                            depth -= 1
                        k += 1
                    if depth == 0:
                        text = content_in[i + 1:j]
                        target_raw = content_in[j + 2:k - 1]
                        original = content_in[i:k]
                        result.append(replace_md_link(text, target_raw, original))
                        i = k
                        continue
                # Fall through if malformed
            result.append(content_in[i])
            i += 1

        return "".join(result)

    content = replace_markdown_links(content)
    return content


def remove_published_tag(content: str) -> str:
    """Remove #published tag from content."""
    content = re.sub(r'#published\s*\n?', '', content, flags=re.IGNORECASE)
    return content.strip()


def extract_first_line_tags(content: str) -> tuple[list[str], str]:
    """Extract tags from the first line of content and return (tags, cleaned_content).
    
    Tags on the first line are moved to frontmatter, tags elsewhere in the body stay intact.
    """
    lines = content.split('\n')
    if not lines:
        return [], content
    
    first_line = lines[0]
    # Find all tags on the first line (excluding #published which is handled separately)
    tag_pattern = r'#([a-zA-Z][a-zA-Z0-9_-]*)'
    tags = re.findall(tag_pattern, first_line)
    # Filter out 'published' tag
    tags = [tag for tag in tags if tag.lower() != 'published']
    
    if not tags:
        return [], content
    
    # Remove tags from first line
    cleaned_first_line = re.sub(r'#[a-zA-Z][a-zA-Z0-9_-]*\s*', '', first_line).strip()
    
    # Rebuild content - if first line is now empty, skip it
    if cleaned_first_line:
        lines[0] = cleaned_first_line
        cleaned_content = '\n'.join(lines)
    else:
        cleaned_content = '\n'.join(lines[1:])
    
    return tags, cleaned_content


def add_tags_to_frontmatter(frontmatter: str, tags: list[str]) -> str:
    """Add tags to frontmatter, merging with existing tags if any."""
    if not tags:
        return frontmatter
    
    # Check if tags field already exists
    tags_match = re.search(r'^tags:\s*\[([^\]]*)\]', frontmatter, re.MULTILINE)
    if tags_match:
        # Parse existing tags
        existing = [t.strip().strip('"\'') for t in tags_match.group(1).split(',') if t.strip()]
        all_tags = list(set(existing + tags))
        tags_str = ', '.join(all_tags)
        frontmatter = re.sub(r'^tags:\s*\[[^\]]*\]', f'tags: [{tags_str}]', frontmatter, flags=re.MULTILINE)
    else:
        # Check for YAML list style tags
        tags_yaml_match = re.search(r'^tags:\s*\n((?:\s+-\s*.+\n?)+)', frontmatter, re.MULTILINE)
        if tags_yaml_match:
            existing = re.findall(r'-\s*(.+)', tags_yaml_match.group(1))
            all_tags = list(set(existing + tags))
            tags_yaml = '\n'.join([f'  - {t}' for t in all_tags])
            frontmatter = re.sub(r'^tags:\s*\n(?:\s+-\s*.+\n?)+', f'tags:\n{tags_yaml}\n', frontmatter, flags=re.MULTILINE)
        else:
            # No existing tags, add new
            tags_str = ', '.join(tags)
            frontmatter = frontmatter.rstrip() + f'\ntags: [{tags_str}]'
    
    return frontmatter


def prepare_body(
    source_body: str,
    published_names: set[str],
    assets_copied: set[str],
    current_note: str,
) -> tuple[str, int, list[str]]:
    processed_body, asset_count = process_assets(source_body, None, assets_copied)
    processed_body = process_embedded_notes(processed_body, published_names)
    processed_body = process_backlinks(processed_body, published_names, current_note)
    processed_body = remove_published_tag(processed_body)
    first_line_tags, processed_body = extract_first_line_tags(processed_body)
    return processed_body, asset_count, first_line_tags


def merge_content(source_content: str, dest_content: str, published_names: set[str], assets_copied: set[str], filename: str) -> tuple[str, int]:
    """Merge: preserve destination frontmatter (with updated last-modified), update body from source."""
    source_fm, source_body = parse_frontmatter(source_content)
    dest_fm, dest_body = parse_frontmatter(dest_content)
    
    processed_body, asset_count, first_line_tags = prepare_body(
        source_body,
        published_names,
        assets_copied,
        Path(filename).stem,
    )
    
    # Compare processed body with destination body
    # If bodies are identical, we don't want to update the last-modified date
    # or rewrite the file.
    if processed_body == str(dest_body):
        return None, asset_count

    # Keep destination frontmatter if exists, otherwise use source
    if dest_fm:
        fm = update_frontmatter_with_modified(dest_fm)
    elif source_fm:
        fm = update_frontmatter_with_modified(source_fm)
    else:
        fm = generate_new_frontmatter(filename)
        fm = update_frontmatter_with_modified(fm)
    
    # Add first-line tags to frontmatter
    fm = add_tags_to_frontmatter(fm, first_line_tags)
    
    return f"---\n{fm}\n---\n\n{processed_body}", asset_count


def find_markdown_files(directory: Path, skip_dirs: set[str]) -> list[Path]:
    """Find all markdown files, skipping specified directories."""
    files = []
    
    for item in directory.iterdir():
        if item.name in skip_dirs:
            print(f"⊘ Skipping directory: {item.name}")
            continue
        
        if item.is_dir():
            files.extend(find_markdown_files(item, skip_dirs))
        elif item.is_file() and item.suffix.lower() == '.md':
            files.append(item)
    
    return files


def main():
    print("=== Note Sync Script ===")
    print(f"Source: {SOURCE_DIR}")
    print(f"Destination: {DEST_DIR}")
    print(f"Assets: {ASSETS_DIR}")
    print(f"Skipping: {', '.join(SKIP_DIRS)}")
    print(f"Criteria: #published tag")
    print("---\n")
    
    # Find all markdown files
    all_files = find_markdown_files(SOURCE_DIR, SKIP_DIRS)
    print(f"Found {len(all_files)} markdown file(s)\n")
    
    # Get list of published note names for backlink processing
    published_names = get_published_note_names(all_files)
    print(f"Notes with #published = {len(published_names)}\n")
    
    copied = 0
    updated = 0
    skipped = 0
    unchanged = 0
    assets_total = 0
    assets_copied = set()  # Track copied assets to avoid duplicates
    
    for source_file in all_files:
        filename = source_file.name
        dest_file = DEST_DIR / filename
        
        try:
            source_content = source_file.read_text(encoding='utf-8')
            
            # Check if file has #published tag
            if not has_publish_tag(source_content):
                skipped += 1
                continue
            
            if dest_file.exists():
                # Update: preserve frontmatter, update body
                dest_content = dest_file.read_text(encoding='utf-8')
                merged, asset_count = merge_content(source_content, dest_content, published_names, assets_copied, filename)
                
                if merged is None:
                    # No changes detected
                    unchanged += 1
                    # print(f"  Unchanged: {filename}") # Optional: comment out to reduce noise
                else:
                    dest_file.write_text(merged, encoding='utf-8')
                    print(f"↻ Updated: {filename}")
                    updated += 1
                    assets_total += asset_count
            else:
                # New file: copy with processed backlinks, assets, and generated frontmatter
                source_fm, source_body = parse_frontmatter(source_content)
                processed_body, asset_count, first_line_tags = prepare_body(
                    source_body,
                    published_names,
                    assets_copied,
                    source_file.stem,
                )
                
                # Generate or use existing frontmatter
                if source_fm:
                    fm = source_fm
                else:
                    fm = generate_new_frontmatter(filename)
                
                # Add first-line tags to frontmatter
                fm = add_tags_to_frontmatter(fm, first_line_tags)
                
                new_content = f"---\n{fm}\n---\n\n{processed_body}"
                
                dest_file.write_text(new_content, encoding='utf-8')
                print(f"✓ Copied: {filename}")
                copied += 1
                assets_total += asset_count
                
        except Exception as e:
            print(f"✗ Error processing {filename}: {e}")
    
    print("\n---")
    print("Summary:")
    print(f"  ✓ Notes copied: {copied}")
    print(f"  ↻ Notes updated: {updated}")
    print(f"  = Notes unchanged: {unchanged}")
    print(f"  ⊘ Notes skipped: {skipped}")
    print(f"  📁 Assets copied: {assets_total}")
    print(f"\nFiles synced to: {DEST_DIR}")


if __name__ == "__main__":
    main()
