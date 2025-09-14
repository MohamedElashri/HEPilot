#!/usr/bin/env python3
"""
HEPilot arXiv LHCb Adapter - Compatibility Import
This file provides backward compatibility by importing the main adapter class.
"""

# Import the main adapter class from the new modular structure
from adapter import HEPilotArxivAdapter

# Re-export for backward compatibility
__all__ = ['HEPilotArxivAdapter']
