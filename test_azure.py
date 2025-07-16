#!/usr/bin/env python3
"""
Test script for Azure OpenAI configuration
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

# Set environment variable
os.environ["LLM_PROVIDER"] = "azure"

# from model.config import config  # No longer needed

def test_config():
    print("This test is now obsolete. Use run_prompt from model.main instead.")

if __name__ == "__main__":
    test_config() 