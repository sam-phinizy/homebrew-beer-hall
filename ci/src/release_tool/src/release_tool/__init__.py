"""Release automation for beer-hall Homebrew tap tools.

This Dagger module automates the process of creating GitHub releases for tools
in the beer-hall Homebrew tap. It handles tag parsing, script discovery, SHA256
calculation, and GitHub release creation.

Usage:
    dagger call release --tag "tool-name/vX.Y.Z" --source . --token env:GITHUB_TOKEN

The module expects tags in the format: tool-name/vX.Y.Z (e.g., gh-pr2org/v1.0.0)
"""

from .main import ReleaseTool as ReleaseTool
