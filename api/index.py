"""Vercel Python Function entry point for the HedgeKnight FastAPI service."""

from hedgeknight.api import app

__all__ = ["app"]
