"""
Embed help/index.html (and its example images) into index.html.

The app is circulated to field offices as a single offline HTML file. A linked
help page would break the moment that file is forwarded on its own, so the guide
is baked into the app and shown in an iframe.

Run this after ANY edit to help/index.html or help/examples/*.png:

    python inline-help.py

It rewrites only the payload between the HELP-PAYLOAD markers in index.html.
Everything else in index.html is left byte for byte alone.
"""

import base64
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(HERE, "index.html")
HELP = os.path.join(HERE, "help", "index.html")
EXAMPLES = os.path.join(HERE, "help", "examples")

OPEN_TAG = '<script id="help-doc" type="text/plain">'
CLOSE_TAG = "</script>"


def read(path):
    """Read text, preserving the file's own newlines and any BOM."""
    s = io.open(path, encoding="utf-8", newline="").read()
    return s, ("\r\n" if "\r\n" in s else "\n")


def build_payload():
    help_html, _ = read(HELP)
    if help_html.startswith("﻿"):
        help_html = help_html[1:]

    # 1. inline every example image as a data URI
    used = []

    def swap(m):
        name = m.group(1)
        path = os.path.join(EXAMPLES, name)
        if not os.path.exists(path):
            sys.exit("missing image: " + path)
        with open(path, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode("ascii")
        used.append(name)
        return 'src="data:image/png;base64,%s"' % b64

    help_html = re.sub(r'src="examples/([^"]+)"', swap, help_html)
    print("  inlined %d images: %s" % (len(used), ", ".join(used)))

    # 2. drop the "Back to DeshDash" link. Inside the iframe it would navigate
    #    the frame to a path that does not exist; the overlay's Close button is
    #    the way out.
    help_html, n = re.subn(r'<a class="back"[^>]*>.*?</a>\s*', "", help_html, flags=re.S)
    print("  removed %d back-link(s)" % n)

    # 3. the payload lives inside a <script> element, so an inner </script>
    #    would terminate it early. Escape it; the app unescapes on read.
    help_html = help_html.replace("</script>", r"<\/script>")

    return help_html


def main():
    app, eol = read(APP)
    start = app.find(OPEN_TAG)
    if start == -1:
        sys.exit("payload slot not found in index.html (looked for %s)" % OPEN_TAG)
    body_at = start + len(OPEN_TAG)
    end = app.find(CLOSE_TAG, body_at)
    if end == -1:
        sys.exit("unterminated payload slot in index.html")

    payload = build_payload()
    updated = app[:body_at] + payload + app[end:]

    io.open(APP, "w", encoding="utf-8", newline="").write(updated)
    print(
        "  payload %d chars; index.html %d -> %d bytes"
        % (len(payload), len(app), len(updated))
    )


if __name__ == "__main__":
    main()
