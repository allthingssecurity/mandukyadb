#!/usr/bin/env python3
"""
MandukyaDB CLI Launcher
Quick start script for the interactive database shell
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from src.cli import main

if __name__ == "__main__":
    print("🕉️  Welcome to MandukyaDB")
    print("Lightweight relational database inspired by the Mandūkya Upaniṣad")
    print()
    main()