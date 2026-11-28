"""Conservative sentence boundaries for citation validation."""

import re

BOUNDARY = re.compile(
    r"""[.!?]+["'”’)]*(?=\s|$|\[\d+\]|[A-Za-z])|\n+"""
)

POST_CITATIONS = re.compile(
    r"\s*(?:\[\d+\]\s*)+(?:[.!?]+(?=\s|$))?"
)

END_CITATIONS = re.compile(
    r"(?:\[\d+\]\s*)+[.!?]*$"
)


def sentence_units(text):
    start = 0

    while start < len(text):
        match = BOUNDARY.search(text, start)

        if match is None:
            unit = text[start:].strip()

            if unit:
                yield unit

            break

        end = match.end()

        if not match.group().startswith("\n"):
            trailing = POST_CITATIONS.match(text, end)

            if trailing is not None:
                end = trailing.end()

        unit = text[start:end].strip()

        if unit:
            yield unit

        start = end


def has_end_citation(text):
    text = text.strip()
    match = END_CITATIONS.search(text)

    if match is None:
        return False

    content = re.sub(
        r"\[\d+\]",
        "",
        text[:match.start()],
    )

    return bool(re.search(r"\w", content))
