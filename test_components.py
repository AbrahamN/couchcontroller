#!/usr/bin/env python3
"""
Component Test Script (Backward Compatibility Wrapper)

This script is maintained for backward compatibility.
For new installations, use: couchcontroller-test

Tests individual CouchController components to verify installation.
"""

import sys
from couchcontroller.cli.test import main


if __name__ == '__main__':
    sys.exit(main())
