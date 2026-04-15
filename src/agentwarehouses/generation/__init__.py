"""Video generation core — Claude Opus 4.6 prompts + Veo 3.1 video generation."""

from agentwarehouses.generation.claude_prompts import CinematicPromptGenerator
from agentwarehouses.generation.veo_client import VeoClient

__all__ = ["CinematicPromptGenerator", "VeoClient"]
