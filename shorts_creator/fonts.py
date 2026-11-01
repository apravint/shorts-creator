"""Makes the bundled caption fonts visible to FFmpeg's libass through fontconfig."""

import os
import tempfile
from xml.sax.saxutils import escape

FONTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "fonts"))


def register_bundled_fonts() -> None:
    """
    Point fontconfig at assets/fonts for this process and its FFmpeg children.
    The ass filter's fontsdir option alone is not reliable: libass can still select a system font
    when the family is not installed, silently replacing Mukta Malar and breaking Tamil shaping.
    System and user fontconfig rules are left out on purpose, since a desktop's family substitutions
    would otherwise win over the bundled font. System font directories stay available for fallback glyphs.
    """
    if os.environ.get("FONTCONFIG_FILE") or not os.path.isdir(FONTS_DIR):
        return
    font_dirs = [FONTS_DIR, "/usr/share/fonts", "/usr/local/share/fonts", "/System/Library/Fonts", "/Library/Fonts"]
    dir_entries = "".join(f"  <dir>{escape(d)}</dir>\n" for d in font_dirs)
    cache_dir = os.path.join(tempfile.gettempdir(), "shorts_creator_fontcache")
    config = (
        '<?xml version="1.0"?>\n<!DOCTYPE fontconfig SYSTEM "fonts.dtd">\n<fontconfig>\n'
        f"{dir_entries}"
        f"  <cachedir>{escape(cache_dir)}</cachedir>\n"
        "</fontconfig>\n"
    )
    fd, path = tempfile.mkstemp(prefix="shorts_creator_fonts_", suffix=".conf")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(config)
    os.environ["FONTCONFIG_FILE"] = path
