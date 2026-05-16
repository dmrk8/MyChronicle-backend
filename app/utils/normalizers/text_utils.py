# app/utils/text_utils.py
import re
from html.parser import HTMLParser
from typing import List, Optional


def build_slug(normalized_title: str, media_id: int) -> str:
    slug = re.sub(r"[^\w\s-]", "", normalized_title)
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-_")
    return f"{slug or 'media'}-{media_id}"


def normalize_title_text(raw: str) -> str:
    normalized = re.sub(r"[^\w\s]", "", raw).lower()
    return re.sub(r"\s+", " ", normalized).strip()


def build_search_tokens(title: str, synonyms: Optional[List[str]] = None) -> List[str]:
    tokens: set[str] = set()

    def process(text: str) -> None:
        if not text:
            return
        text = re.sub(r"[^\w\s]", "", text.lower())
        tokens.add(text)
        tokens.update(text.split())

    process(title)
    for syn in synonyms or []:
        process(syn)

    return list(tokens)


def strip_html(text: Optional[str]) -> Optional[str]:
    if not text:
        return None

    class HTMLStripper(HTMLParser):
        def __init__(self):
            super().__init__()
            self.reset()
            self.fed = []

        def handle_data(self, data: str) -> None:
            self.fed.append(data)

        def get_data(self) -> str:
            return "".join(self.fed)

    stripper = HTMLStripper()
    try:
        stripper.feed(text)
        result = stripper.get_data()
        # Clean up extra whitespace
        result = re.sub(r"\s+", " ", result).strip()
        return result
    except Exception:
        # Fallback to regex if parsing fails
        return re.sub(r"<[^>]+>", "", text).strip()
