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
        
        # Skip if it's a note link (no extension or .md)
        if '.' not in asset_name or asset_name.endswith('.md'):
            return match.group(0)
        
        # Find the asset in source
        asset_path = find_asset_in_source(asset_name, SOURCE_DIR, SKIP_DIRS)
        if asset_path and asset_path.suffix.lower() in ASSET_EXTENSIONS:
            dest_asset = ASSETS_DIR / asset_name
            if asset_name not in assets_copied:
                shutil.copy2(asset_path, dest_asset)
                assets_copied.add(asset_name)
                copied_count += 1
            # Update to relative path
            return f"![{asset_name}](./assets/{asset_name})"
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


def process_backlinks(content: str, published_names: set[str]) -> str:
    """Keep backlinks only if target is also published, otherwise remove.
    
    PRIMARY CONDITION: Only keep backlinks to notes that have #published tag.
    The published_names set contains only filenames (stems) of notes with #published.
    
    SECONDARY CONDITION: Strip heading anchors before comparison.
    Links like [[Note#Section|Display]] should match if "Note" is published,
    even though the full link text includes "#Section".
    """
    def replace_link(match):
        link = match.group(1).strip()
        display = match.group(2)
        
        # Strip heading anchor (e.g., "Note#Section" -> "Note") for comparison
        # This ensures [[Static Site Generator#Heading|text]] matches "Static Site Generator"
        base_link = link.split('#')[0].strip()
        
        # If base_link is empty (e.g., [[#^blockid]]), it's an internal Obsidian block reference
        # These don't work in Quartz, so remove them entirely
        if not base_link:
            return ''
        
        # Check if the base note (without anchor) is in published notes
        if base_link in published_names:
            return match.group(0)  # Keep the backlink (including anchor)
        # Remove backlink, keep display text or link name
        return display[1:] if display else link
    
    # Handle [[link]] or [[link|display]]
    return re.sub(r'\[\[([^\]|]+)(\|[^\]]+)?\]\]', replace_link, content)


def remove_published_tag(content: str) -> str:
    """Remove #published tag from content."""
    # Remove #published with optional trailing whitespace/newline
    content = re.sub(r'#published\s*\n?', '', content, flags=re.IGNORECASE)
    # Clean up any resulting empty lines
    content = re.sub(r'\n\n\n+', '\n\n', content)
    return content.strip()


def merge_content(source_content: str, dest_content: str, published_names: set[str], assets_copied: set[str], filename: str) -> tuple[str, int]:
    """Merge: preserve destination frontmatter (with updated last-modified), update body from source."""
    source_fm, source_body = parse_frontmatter(source_content)
    dest_fm, dest_body = parse_frontmatter(dest_content)
    
    # Process assets, backlinks, and remove #published tag from source body
    processed_body, asset_count = process_assets(source_body, None, assets_copied)
    processed_body = process_backlinks(processed_body, published_names)
    processed_body = remove_published_tag(processed_body)
    
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
                processed_body, asset_count = process_assets(source_body, source_file, assets_copied)
                processed_body = process_backlinks(processed_body, published_names)
                processed_body = remove_published_tag(processed_body)
                
                # Generate or use existing frontmatter
                if source_fm:
                    fm = source_fm
                else:
                    fm = generate_new_frontmatter(filename)
                
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
