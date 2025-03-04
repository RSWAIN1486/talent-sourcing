"""
Security module for authentication and authorization.
This module re-exports necessary security functions from the appropriate modules.
"""

from app.api.deps import get_current_user

__all__ = ["get_current_user"] 