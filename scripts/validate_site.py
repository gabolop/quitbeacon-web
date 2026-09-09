"""Small dependency-free checks for the public QuitBeacon static site."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = ["index.html", "privacy.html", "support.html", "404.html"]
TRACKING_MARKERS = (
    "googletagmanager",
    "google-analytics",
    "plausible.io",
    "segment.com",
    "facebook.net",
    "hotjar.com",
)


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, {key: value or "" for key, value in attrs}))


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def local_target_exists(href: str) -> bool:
    path = urlsplit(href).path.lstrip("/")
    if not path:
        path = "index.html"
    if path.endswith("/"):
        path += "index.html"
    return (ROOT / path).is_file()


def validate_html(filename: str) -> None:
    source = (ROOT / filename).read_text(encoding="utf-8")
    lowered = source.lower()
    for marker in TRACKING_MARKERS:
        if marker in lowered:
            fail(f"{filename} contains an unreviewed tracking marker: {marker}")

    parser = SiteParser()
    parser.feed(source)
    tags = parser.tags
    if not any(tag == "html" and attrs.get("lang") for tag, attrs in tags):
        fail(f"{filename} is missing an html lang attribute")
    if not any(tag == "title" for tag, _ in tags):
        fail(f"{filename} is missing a title")
    if not any(tag == "meta" and attrs.get("name") == "viewport" for tag, attrs in tags):
        fail(f"{filename} is missing a viewport meta tag")
    if not any(tag == "link" and attrs.get("href") == "/styles.css" for tag, attrs in tags):
        fail(f"{filename} is missing the shared stylesheet")
    if filename in {"index.html", "privacy.html", "support.html"}:
        if not any(
            tag == "select" and attrs.get("id") == "language-select"
            for tag, attrs in tags
        ):
            fail(f"{filename} is missing the language selector")
        if not any(
            tag == "script" and attrs.get("src") == "/script.js"
            for tag, attrs in tags
        ):
            fail(f"{filename} is missing the localization script")

    for tag, attrs in tags:
        target = attrs.get("href", "") if tag == "a" else attrs.get("src", "")
        if not target or target.startswith(("#", "mailto:", "http://", "https://", "javascript:")):
            continue
        if not local_target_exists(target):
            fail(f"{filename} references missing local target: {target}")


def validate_metadata() -> None:
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap: https://quitbeacon-web.pages.dev/sitemap.xml" not in robots:
        fail("robots.txt does not point to the live sitemap")

    try:
        sitemap = ET.parse(ROOT / "sitemap.xml")
    except ET.ParseError as error:
        fail(f"sitemap.xml is not valid XML: {error}")
    urls = [element[0].text or "" for element in sitemap.getroot() if len(element) > 0]
    if not urls or any("quitbeacon-web.pages.dev" not in url for url in urls):
        fail("sitemap.xml contains an unexpected URL")


for html_file in HTML_FILES:
    if not (ROOT / html_file).is_file():
        fail(f"missing required page: {html_file}")
    validate_html(html_file)

validate_metadata()
print(f"Validated {len(HTML_FILES)} pages, local links, and deployment metadata.")
