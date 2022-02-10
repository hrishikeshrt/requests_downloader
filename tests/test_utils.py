#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for `requests_downloader.utils`."""

from requests_downloader.utils import md5sum

###############################################################################


def test_md5sum(tmp_path):
    tmp_file = tmp_path / "test.txt"
    tmp_file.write_text("hello world\n")
    assert "6f5902ac237024bdd0c176cb93063dc4" == md5sum(tmp_file)
