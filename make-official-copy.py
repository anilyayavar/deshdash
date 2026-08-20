"""
Produce the OFFICIAL copy of DeshDash from this repo's index.html.

This repo is the author's own copy. Its signature carries a personal LinkedIn
link and makes no claim on behalf of the office.

The official copy is different in exactly one respect, the signature. The
personal link is removed outright, not hidden, so that the file circulated to
field offices contains no personal link anywhere in it, even when opened in a
text editor. In its place the signature names the office.

Run this whenever a release is cut:

    python make-official-copy.py
    python make-official-copy.py "..\\distribution-papers\\DeshDash v1.0.html"

Nothing else in the file is touched. Run inline-help.py first if the guide has
changed, since this reads index.html as it stands.
"""

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "index.html")
DEFAULT_OUT = os.path.abspath(
    os.path.join(HERE, "..", "distribution-papers", "DeshDash v1.0.html")
)

OFFICE = "for CDMA"

PERSONAL = (
    '    Developed by <strong style="color:#8aabff">Anil Kumar Goyal</strong> &middot;\n'
    '    <a href="https://www.linkedin.com/in/anil-kumar-goyal/" target="_blank"'
    ' rel="noopener" style="color:#8aabff;text-decoration:none">LinkedIn</a>'
)

OFFICIAL = (
    '    Developed by <strong style="color:#8aabff">Anil Kumar Goyal</strong>'
    " &middot; " + OFFICE
)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT

    s = io.open(SOURCE, encoding="utf-8", newline="").read()
    eol = "\r\n" if "\r\n" in s else "\n"

    personal = PERSONAL.replace("\n", eol)
    if s.count(personal) != 1:
        sys.exit(
            "signature block not found as expected in index.html (%d matches).\n"
            "If the signature was edited by hand, update PERSONAL in this script."
            % s.count(personal)
        )

    s = s.replace(personal, OFFICIAL.replace("\n", eol))

    # Nothing personal may survive into a file going out under the Director's
    # signature. Fail loudly rather than ship a file that still contains it.
    for term in ("linkedin.com", "linkedin"):
        if term.lower() in s.lower():
            sys.exit("refusing to write: '%s' still present in the official copy" % term)

    outdir = os.path.dirname(out)
    if outdir and not os.path.isdir(outdir):
        os.makedirs(outdir)
    io.open(out, "w", encoding="utf-8", newline="").write(s)

    print("  source   %s" % SOURCE)
    print("  official %s" % out)
    print("  signature now reads: Developed by Anil Kumar Goyal, %s" % OFFICE)
    print("  personal link present in official copy: no")
    print("  %d bytes" % os.path.getsize(out))


if __name__ == "__main__":
    main()
