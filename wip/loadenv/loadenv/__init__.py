#!/usr/bin/env python
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
Init script for the LoadEnv package
"""
from .version import __version__

from pathlib import Path
import sys
sys.path.insert(0, Path("..").resolve())

from load_env import LoadEnv
