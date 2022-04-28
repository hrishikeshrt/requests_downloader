#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility Functions"""

import hashlib

###############################################################################


def md5sum(file, block_size=4096):
    """Calculate the md5sum for a file.

    Parameters
    ----------
    file : str
        Filename.
    block_size : int
        Block size to use when reading.

    Returns
    -------
    checksum : str
        The hexadecimal md5 checksum of the file.
    """
    md5 = hashlib.md5()
    with open(file, "rb") as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


###############################################################################
