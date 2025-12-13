#!/usr/bin/env python3
"""
CouchController Client Application (Backward Compatibility Wrapper)

This script is maintained for backward compatibility.
For new installations, use: couchcontroller-client

Runs on the remote player's machine.
Captures controller input, displays host's screen.
"""

import sys
from couchcontroller.cli.client import main


if __name__ == '__main__':
    sys.exit(main())
