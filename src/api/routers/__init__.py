"""
API Routers Package
"""
from .biographies import router as biographies_router
from .sources import router as sources_router
from .collections import router as collections_router

__all__ = [
    "biographies_router",
    "sources_router",
    "collections_router",
]
