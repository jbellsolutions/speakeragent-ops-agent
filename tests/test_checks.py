from __future__ import annotations

from app.checks import extract_links


def test_extract_links_normalizes_and_filters():
    html = """
    <a href="/a">A</a>
    <a href="mailto:test@example.com">Email</a>
    <a href="#top">Top</a>
    <a href="https://example.com/b#fragment">B</a>
    <a href="/a">Duplicate</a>
    """
    assert extract_links("https://example.com", html, 10) == [
        "https://example.com/a",
        "https://example.com/b",
    ]

