"""GSD ADK Web Application package exposing `root_agent`."""

from . import agent
from .agent import build_root_agent, root_agent

__all__ = ["agent", "root_agent", "build_root_agent"]

