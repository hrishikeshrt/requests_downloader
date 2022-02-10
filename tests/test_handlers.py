#!/usr/bin/env python
"""Tests for `requests_downloader.handlers`."""

from requests_downloader.handlers import handle_url


def test_handle_url():
    url_result = {
        'https://drive.google.com/file/d/<file_id>/view': [
            ('drive', 'https://drive.google.com/u/0/uc?id=<file_id>&export=download')
        ],
        'https://drive.google.com/file/d/<file_id>/view?usp=sharing': [
            ('drive', 'https://drive.google.com/u/0/uc?id=<file_id>&export=download')
        ],
        'https://www.dropbox.com/s/<file_id>/<file_name>': [
            ('dropbox', 'https://www.dropbox.com/s/<file_id>/<file_name>?dl=1')
        ],
        'https://www.dropbox.com/s/<file_id>/<file_name>?dl=0': [
            ('dropbox', 'https://www.dropbox.com/s/<file_id>/<file_name>?dl=1')
        ],
        'https://www.dropbox.com/s/<file_id>/<file_name>?dl=0&opt=val': [
            ('dropbox', 'https://www.dropbox.com/s/<file_id>/<file_name>?dl=1&opt=val')
        ],
    }
    for url, url_result in url_result.items():
        assert handle_url(url) == (url_result, 0)
