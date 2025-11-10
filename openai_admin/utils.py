"""Utility functions for OpenAI Admin CLI"""
from typing import Optional
from datetime import datetime


def format_timestamp(ts: Optional[int]) -> str:
    """Format Unix timestamp to readable date"""
    if ts is None:
        return "N/A"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def format_redacted_value(value: str) -> str:
    """Format redacted API key value to be more compact"""
    if not value:
        return "N/A"
    # Replace long strings of asterisks (4 or more) with just 5 stars
    import re
    shortened = re.sub(r'\*{4,}', '*****', value)
    return shortened
