"""
Film & Animated Movie Generator Module.
"""

from .film_pipeline import generate_animated_film
from .screenplay import ANIMATION_STYLES, get_screenplay
from .art_generator import generate_scene_image
from .animator import animate_scene_shot
from .movie_compositor import assemble_animated_movie

__all__ = [
    "generate_animated_film",
    "ANIMATION_STYLES",
    "get_screenplay",
    "generate_scene_image",
    "animate_scene_shot",
    "assemble_animated_movie",
]
