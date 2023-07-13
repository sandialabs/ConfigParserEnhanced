#!/usr/bin/env python
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
Init script for the SetEnvironment package
"""
from .version import __version__

from .SetEnvironment import envvar_find_in_path
from .SetEnvironment import envvar_op
from .SetEnvironment import envvar_set
from .SetEnvironment import envvar_set_if_empty

from .SetEnvironment import SetEnvironment
