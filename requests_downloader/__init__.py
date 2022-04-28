#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
requests_downloader

Python package to download files
"""

###############################################################################

__author__ = """Hrishikesh Terdalkar"""
__email__ = "hrishikeshrt@linuxmail.org"
__version__ = "0.4.0"

###############################################################################

from .downloader import download  # noqa
from .handlers import handle_url  # noqa
from .utils import md5sum  # noqa
