#!/usr/bin/env python3
"""
OpenAI Admin CLI - Main entry point wrapper

The codebase has been refactored into a modular structure:
- openai_admin/client.py - API client
- openai_admin/utils.py - Utility functions
- openai_admin/commands/ - Command modules
- cli.py - Main CLI entry point

This file serves as a convenience wrapper for backward compatibility.
"""

from cli import cli

if __name__ == '__main__':
    cli()
