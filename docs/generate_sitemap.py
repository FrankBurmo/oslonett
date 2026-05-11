#!/usr/bin/env python3
"""
Genererer sitemap.xml for www.oslo.net.

Kjøres fra rotmappen i prosjektet:
    python docs/generate_sitemap.py

Skriptet traverserer alle .html-filer, ekskluderer ikke-offentlige
mapper og produserer en gyldig sitemap.xml i XML Sitemap Protocol 0.9-format.
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

# -----------------------------------------------------------------------
# Konfigurasjon
# -----------------------------------------------------------------------

BASE_URL = "https://www.oslo.net"

# Mapper som ikke skal inkluderes i sitemappen
EXCLUDED_DIRS = {
    "docs",      # intern dokumentasjon
    "cgi",       # CGI-skript, ikke HTML-sider
    "gifs",      # bilderessurser
    "graphics",  # bilderessurser
    "img",       # bilderessurser
    "css",       # stilarkressurser
    "js",        # JavaScript-ressurser
    ".git",      # versjonskontroll
}

# -----------------------------------------------------------------------


def find_html_files(root: Path) -> list[Path]:
    """Returnerer alle .html-filer under root, sortert, med eksklusjoner."""
    result = []
    for path in sorted(root.rglob("*.html")):
        parts = path.relative_to(root).parts
        # Ekskluder filer i forbudte mapper (på alle nivåer)
        if any(part in EXCLUDED_DIRS for part in parts[:-1]):
            continue
        result.append(path)
    return result


def get_lastmod(path: Path) -> str:
    """Returnerer ISO 8601-dato for filen (W3C Datetime, dato-presisjon)."""
    mtime = path.stat().st_mtime
    dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")


def path_to_url(root: Path, path: Path) -> str:
    """Konverterer en absolutt filsti til en URL."""
    rel = path.relative_to(root)
    # Bruk forward slash uavhengig av OS
    url_path = "/".join(rel.parts)
    return f"{BASE_URL}/{url_path}"


def build_sitemap(root: Path) -> ET.ElementTree:
    """Bygger XML-treet for sitemap.xml."""
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)

    urlset = ET.Element(f"{{{namespace}}}urlset")

    html_files = find_html_files(root)

    for path in html_files:
        url_el = ET.SubElement(urlset, f"{{{namespace}}}url")

        loc = ET.SubElement(url_el, f"{{{namespace}}}loc")
        loc.text = path_to_url(root, path)

        lastmod = ET.SubElement(url_el, f"{{{namespace}}}lastmod")
        lastmod.text = get_lastmod(path)

    return ET.ElementTree(urlset)


def write_sitemap(tree: ET.ElementTree, output: Path) -> None:
    """Skriver XML til fil med XML-deklarasjon og innrykk (Python 3.9+)."""
    ET.indent(tree, space="  ")
    tree.write(
        str(output),
        xml_declaration=True,
        encoding="utf-8",
        short_empty_elements=False,
    )


def main() -> None:
    root = Path(__file__).parent.parent.resolve()
    output = root / "sitemap.xml"

    print(f"Søker etter HTML-filer under: {root}")
    html_files = find_html_files(root)
    print(f"Fant {len(html_files)} HTML-filer")

    tree = build_sitemap(root)
    write_sitemap(tree, output)

    print(f"Skrev {output}")


if __name__ == "__main__":
    main()
