"""
Analyse av brutte lenker og ubrukte ressurser i Oslonett-repoet.
Kjøres fra repo-roten eller docs/-mappen.
"""

import os
import re
import json
from pathlib import Path
from urllib.parse import urlparse, unquote

REPO_ROOT = Path(__file__).parent.parent.resolve()

# Mapper og filer som hoppes over i analysen
SKIP_DIRS = {'.git', 'docs'}
SKIP_FILES = {'_link_audit.py'}

# Filer vi sjekker for lenker
HTML_EXTENSIONS = {'.html', '.htm', '.cgi', '.pl', '.css', '.js'}
RESOURCE_EXTENSIONS = {
    '.html', '.htm', '.gif', '.jpg', '.jpeg', '.png', '.css', '.js',
    '.xbm', '.ppm', '.ico', '.pdf', '.txt', '.cgi', '.pl', '.json',
    '.map', '.svg', '.webp', '.mov', '.avi', '.mp3', '.wav', '.zip',
}

# Regex for å plukke ut URL-attributter fra HTML
ATTR_PATTERN = re.compile(
    r'''(?:href|src|action|data|background|usemap|lowsrc)\s*=\s*['"](.*?)['"]''',
    re.IGNORECASE
)
# SSI includes
SSI_PATTERN = re.compile(
    r'''<!--#include\s+(?:file|virtual)="(.*?)"''',
    re.IGNORECASE
)
# CSS url(...)
CSS_URL_PATTERN = re.compile(
    r'''url\s*\(\s*['"](.*?)['"]\s*\)''',
    re.IGNORECASE
)
CSS_URL_NOQUOTE = re.compile(
    r'''url\s*\(\s*([^'")\s]+)\s*\)''',
    re.IGNORECASE
)

def is_external(url: str) -> bool:
    """Returner True hvis URL er ekstern (http, https, ftp, mailto, javascript, data:)."""
    lower = url.lower().strip()
    return lower.startswith(('http://', 'https://', 'ftp://', 'mailto:', 'javascript:', 'data:', '#', '//'))

def normalize_url(url: str, current_file: Path) -> Path | None:
    """
    Konverter en URL til en absolutt Path innen repoet.
    Returnerer None hvis URL er ekstern, anker-only, eller ikke kan resolves.
    """
    url = url.strip()
    if not url or is_external(url):
        return None
    
    # Fjern query-string og anker
    url = re.split(r'[?#]', url)[0]
    if not url:
        return None
    
    # URL-decode
    url = unquote(url)
    
    # Normaliser path-separatorer
    url = url.replace('\\', '/')
    
    if url.startswith('/'):
        # Root-relativ: relativ til REPO_ROOT
        return (REPO_ROOT / url.lstrip('/')).resolve()
    else:
        # Relativ til current file
        return (current_file.parent / url).resolve()

def collect_all_files() -> set[Path]:
    """Samler alle filer i repoet (eksklusive SKIP_DIRS og SKIP_FILES)."""
    all_files = set()
    for root, dirs, files in os.walk(REPO_ROOT):
        root_path = Path(root)
        # Fjern skip-mapper in-place
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            if fname in SKIP_FILES:
                continue
            fpath = root_path / fname
            all_files.add(fpath.resolve())
    return all_files

def extract_refs_from_file(fpath: Path) -> list[tuple[str, int]]:
    """
    Trekker ut alle ressursreferanser fra en fil.
    Returnerer liste av (url, linjenummer).
    """
    refs = []
    try:
        text = fpath.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return refs
    
    suffix = fpath.suffix.lower()
    
    lines = text.splitlines()
    for lineno, line in enumerate(lines, 1):
        if suffix in ('.html', '.htm', '.cgi', '.pl'):
            for m in ATTR_PATTERN.finditer(line):
                refs.append((m.group(1), lineno))
            for m in SSI_PATTERN.finditer(line):
                refs.append((m.group(1), lineno))
        if suffix == '.css' or suffix in ('.html', '.htm'):
            for m in CSS_URL_PATTERN.finditer(line):
                refs.append((m.group(1), lineno))
            for m in CSS_URL_NOQUOTE.finditer(line):
                refs.append((m.group(1), lineno))
    
    return refs

def run_audit():
    print(f"[INFO] Repo-rot: {REPO_ROOT}")
    
    all_files = collect_all_files()
    print(f"[INFO] Filer funnet: {len(all_files)}")
    
    # Alle filer vi vil analysere for lenker
    source_files = {f for f in all_files if f.suffix.lower() in HTML_EXTENSIONS}
    print(f"[INFO] Kildefiler (HTML/CSS/JS/CGI): {len(source_files)}")
    
    # --- Trinn 1: Finn brutte interne referanser ---
    broken_refs = []      # (kilde_rel, url_raw, linjenr)
    all_referenced = set()  # absolutte paths av alle refererte ressurser

    for src_file in sorted(source_files):
        refs = extract_refs_from_file(src_file)
        for url_raw, lineno in refs:
            if is_external(url_raw):
                continue
            resolved = normalize_url(url_raw, src_file)
            if resolved is None:
                continue
            all_referenced.add(resolved)
            if not resolved.exists():
                rel_src = src_file.relative_to(REPO_ROOT)
                broken_refs.append((str(rel_src), url_raw, lineno, str(resolved.relative_to(REPO_ROOT) if resolved.is_relative_to(REPO_ROOT) else resolved)))

    # --- Trinn 2: Finn ubrukte ressurser ---
    resource_files = {f for f in all_files if f.suffix.lower() in RESOURCE_EXTENSIONS}
    unreferenced = resource_files - all_referenced
    
    # Filtrer bort kildefiler som er entry points (index.html etc.) — de trenger ikke å være referert
    # men vi tar med alt og lar rapporten sortere
    
    return {
        'broken': sorted(broken_refs, key=lambda x: x[0]),
        'unreferenced': sorted(str(f.relative_to(REPO_ROOT)) for f in unreferenced),
        'total_files': len(all_files),
        'source_files': len(source_files),
        'resource_files': len(resource_files),
        'total_refs': len(all_referenced),
    }

if __name__ == '__main__':
    result = run_audit()
    
    print(f"\n=== BRUTTE REFERANSER ({len(result['broken'])}) ===")
    prev_src = None
    for src, url, lineno, resolved in result['broken']:
        if src != prev_src:
            print(f"\n  [{src}]")
            prev_src = src
        print(f"    L{lineno}: {url!r}  →  {resolved}")
    
    print(f"\n=== UBRUKTE RESSURSER ({len(result['unreferenced'])}) ===")
    for f in result['unreferenced']:
        print(f"  {f}")
    
    print(f"\n=== SAMMENDRAG ===")
    print(f"  Totalt filer: {result['total_files']}")
    print(f"  Kildefiler analysert: {result['source_files']}")
    print(f"  Ressursfiler: {result['resource_files']}")
    print(f"  Brutte referanser: {len(result['broken'])}")
    print(f"  Ubrukte ressurser: {len(result['unreferenced'])}")
    
    # Lagre råresultat til JSON for videre bruk
    output = {
        'broken': [{'src': s, 'url': u, 'line': l, 'resolved': r} for s,u,l,r in result['broken']],
        'unreferenced': result['unreferenced'],
        'stats': {
            'total_files': result['total_files'],
            'source_files': result['source_files'],
            'resource_files': result['resource_files'],
            'broken_count': len(result['broken']),
            'unreferenced_count': len(result['unreferenced']),
        }
    }
    out_path = Path(__file__).parent / '_audit_result.json'
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n[INFO] Rådata lagret: {out_path}")
