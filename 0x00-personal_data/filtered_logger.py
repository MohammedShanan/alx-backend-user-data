#!/usr/bin/env python3
"""A module for filtering logs"""
import re
from typing import List

def filter_datum(
    fields: List[str],
    redaction: str,
    message: str,
    separator: str,
) -> str:
    """Filters a log line"""
    pattern = f"({'|'.join(fields)})=[^ {separator}]*"
    return re.sub(pattern, lambda m: f"{m.group(1)}={redaction}", message)
