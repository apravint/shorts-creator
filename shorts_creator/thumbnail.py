"""
High-CTR YouTube Thumbnail & Visual Cover Engine for ShortsCreator AI.
Generates attention-grabbing 1080x1920 (Vertical Shorts) and 1280x720 (Landscape)
thumbnails with gradient overlays, badge pills, bold typography, and bullet points.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "fonts"))


def get_thumbnail_fonts(size: int = 40):
    """Load bold MuktaMalar or fallback TTF font."""
    font_bold = os.path.join(FONTS_DIR, "MuktaMalar-ExtraBold.ttf")
    if not os.path.isfile(font_bold):
        font_bold = os.path.join(FONTS_DIR, "MuktaMalar-Bold.ttf")
    
    if os.path.isfile(font_bold):
        try:
            return ImageFont.truetype(font_bold, size)
        except Exception:
            pass
    try:
        return ImageFont.load_default()
    except Exception:
        return None


def wrap_text_simple(text: str, font: Any, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    curr = []
    for w in words:
        test_line = " ".join(curr + [w])
        bbox = draw.textbbox((0, 0), test_line, font=font) if font else (0, 0, len(test_line) * 12, 20)
        w_px = bbox[2] - bbox[0]
        if w_px <= max_width:
            curr.append(w)
        else:
            if curr:
                lines.append(" ".join(curr))
            curr = [w]
    if curr:
        lines.append(" ".join(curr))
    return lines or [text]


def generate_thumbnail(
    title: str,
    output_path: str,
    bullets: Optional[List[str]] = None,
    is_shorts: bool = True,
    badge: Optional[str] = None,
    theme: Optional[str] = "cyber"
) -> str:
    """Generate high-CTR thumbnail for YouTube Shorts or widescreen video."""
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    w, h = (1080, 1920) if is_shorts else (1280, 720)
    bullets = bullets or ["Core Breakdown", "Actionable Insight", "Full Explanation"]

    # Color themes
    if theme in ("fire", "red"):
        bg_color = (26, 5, 5, 255)
        accent_color = (239, 68, 68, 255)
        sec_color = (251, 146, 60, 255)
    elif theme in ("gold", "yellow"):
        bg_color = (24, 18, 5, 255)
        accent_color = (234, 179, 8, 255)
        sec_color = (253, 224, 71, 255)
    elif theme in ("emerald", "green"):
        bg_color = (4, 30, 20, 255)
        accent_color = (16, 185, 129, 255)
        sec_color = (52, 211, 153, 255)
    else:  # cyber / cosmic / default
        bg_color = (15, 23, 42, 255)
        accent_color = (59, 130, 246, 255)
        sec_color = (14, 165, 233, 255)

    img = Image.new("RGBA", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    # Top gradient glow stripe
    stripe_height = 14 if is_shorts else 8
    for x in range(w):
        r = int(accent_color[0] + (sec_color[0] - accent_color[0]) * (x / max(1, w)))
        g = int(accent_color[1] + (sec_color[1] - accent_color[1]) * (x / max(1, w)))
        b = int(accent_color[2] + (sec_color[2] - accent_color[2]) * (x / max(1, w)))
        draw.line([(x, 0), (x, stripe_height)], fill=(r, g, b, 255), width=1)

    badge_text = badge or ("★ YOUTUBE SHORTS" if is_shorts else "★ FEATURED SHOWCASE")

    if is_shorts:
        # Vertical Shorts Layout (1080x1920)
        # Main content card
        draw.rectangle((50, 320, w - 50, 1550), fill=(16, 24, 45), outline=accent_color, width=4)

        # Red category badge
        draw.rectangle((90, 380, 500, 440), fill=(220, 38, 38))
        f_badge = get_thumbnail_fonts(24)
        draw.text((110, 395), badge_text, fill=(255, 255, 255), font=f_badge)

        # Big Title
        clean_title = title.replace("#Shorts", "").replace("#shorts", "").strip()
        f_title = get_thumbnail_fonts(52)
        title_lines = wrap_text_simple(clean_title, f_title, 880, draw)
        y = 480
        for i, line in enumerate(title_lines[:3]):
            col = (255, 255, 255) if i == 0 else (255, 215, 0)
            draw.text((90, y), line, fill=col, font=f_title)
            y += 85

        # Sub-header banner
        draw.rectangle((90, 780, w - 90, 860), fill=(24, 38, 68), outline=sec_color, width=2)
        f_sub = get_thumbnail_fonts(28)
        draw.text((120, 804), "🔥 60 SECONDS EXPLAINER", fill=(255, 255, 255), font=f_sub)

        # Bullet points
        cy = 930
        f_bullet = get_thumbnail_fonts(30)
        for b in bullets[:4]:
            draw.text((90, cy), f"⚡ {b[:36]}", fill=(210, 235, 255), font=f_bullet)
            cy += 90

    else:
        # Landscape 16:9 Layout (1280x720)
        draw.rectangle((50, 60, 680, 660), fill=(16, 24, 45), outline=accent_color, width=3)
        draw.rectangle((80, 95, 380, 145), fill=(220, 38, 38))
        f_badge = get_thumbnail_fonts(22)
        draw.text((95, 107), badge_text, fill=(255, 255, 255), font=f_badge)

        clean_title = title.replace("#Shorts", "").replace("#shorts", "").strip()
        f_title = get_thumbnail_fonts(42)
        title_lines = wrap_text_simple(clean_title, f_title, 560, draw)
        y = 180
        for i, line in enumerate(title_lines[:2]):
            col = (255, 255, 255) if i == 0 else (255, 215, 0)
            draw.text((80, y), line, fill=col, font=f_title)
            y += 70

        draw.rectangle((720, 60, 1220, 660), fill=(14, 20, 38), outline=sec_color, width=2)
        draw.text((750, 100), "KEY TAKEAWAYS:", fill=(255, 255, 255), font=f_badge)

        cy = 160
        f_bullet = get_thumbnail_fonts(24)
        for b in bullets[:5]:
            draw.text((750, cy), f"⚡ {b[:32]}", fill=(200, 225, 255), font=f_bullet)
            cy += 65

    # Outer border accent
    draw.rectangle((0, 0, w - 1, h - 1), outline=accent_color, width=4)
    img.save(str(out_file))
    return str(out_file)
