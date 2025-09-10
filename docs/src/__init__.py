"""
MandukyaDB - A lightweight relational database inspired by the Mandūkya Upaniṣad

The four states of consciousness:
- Jagrat (Waking): Storage layer
- Swapna (Dreaming): Query planner  
- Sushupti (Deep Sleep): Memory cache
- Turiya (Pure Consciousness): Execution engine
"""

from .mandukya_db import MandukyaDB
from .exceptions import MandukyaError, ParseError, ExecutionError

__version__ = "1.0.0"
__author__ = "MandukyaDB Team"

__all__ = ["MandukyaDB", "MandukyaError", "ParseError", "ExecutionError"]

