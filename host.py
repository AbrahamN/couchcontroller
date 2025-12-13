#!/usr/bin/env python3
"""
CouchController Host Application (Backward Compatibility Wrapper)

This script is maintained for backward compatibility.
For new installations, use: couchcontroller-host

Runs on the machine with the game.
Captures screen, creates virtual controllers, and streams to clients.
"""

import sys
from couchcontroller.cli.host import main

if __name__ == '__main__':
    sys.exit(main())
