"""
ShortsCreator AI 2.0 - Universal AI Video & Film Engine (Tamil & English).
Autonomous production-grade video engine featuring multi-model generative AI,
Shotcraft recipe physics, developer codebase 'brag' showcases, digital talking avatars,
and studio EBU R128 audio mastering.
"""

__version__ = "2.0.0"
__author__ = "Pravin"

from .video_engine import assemble_shorts_video
from .video_fetcher import get_open_source_video
from .ai_video import AIVideoHub
from .shotcraft import get_shot_recipe, build_recipe_filter, SHOT_RECIPES
from .soundscape import SoundscapeEngine
from .sfx import SoundEffectsSynthesizer
from .avatar import AvatarEngine
from .thumbnail import generate_thumbnail
from .brag import BragHarvester, ViralHookGenerator
from .exploded_engine import ExplodedCADVideoEngine, PIXEL_TENSOR_HARDWARE_PRESET
