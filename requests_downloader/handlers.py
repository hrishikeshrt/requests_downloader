#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Special URL Handlers
"""


import re
import logging
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

###############################################################################

LOGGER = logging.getLogger(__name__)

###############################################################################


def handle_url(url):
    """
    Infer the actual download URLs by handling various special cases

    Parameters
    ----------
    url : str
        Provided download URL.

    Returns
    -------
    urls : list
        List of inferred download URLs from the provided URL.
    default_idx: int
        Index of default URL to download.
    """
    default_idx = 0
    drive = "https://drive.google.com"
    drive_pattern_1 = rf"{drive}/file/d/([^\/]*)/.*"
    drive_match_1 = re.match(drive_pattern_1, url)
    if drive_match_1:
        LOGGER.debug("Google Drive pattern-1 matched.")
        file_id = drive_match_1.group(1)
        dl_url = f"{drive}/u/0/uc?id={file_id}&export=download"
        return [("drive", dl_url)], default_idx

    drive_pattern_2 = rf"{drive}/open\?id=([^\/&]*).*"
    drive_match_2 = re.match(drive_pattern_2, url)
    if drive_match_2:
        LOGGER.debug("Google Drive pattern-2 matched.")
        file_id = drive_match_2.group(1)
        dl_url = f"{drive}/u/0/uc?id={file_id}&export=download"
        return [("drive", dl_url)], default_idx

    docs = "https://docs.google.com"
    preference = {
        "spreadsheets": ["xlsx", "ods", "pdf"],
        "document": ["docx", "odt", "pdf"],
        "presentation": ["pptx", "odp", "pdf"],
    }
    doc_pattern = rf"{docs}/(spreadsheets|document|presentation)/d/([^\/]*)/.*"
    doc_match = re.match(doc_pattern, url)
    if doc_match:
        LOGGER.debug("Google Docs pattern matched.")
        doc_type = doc_match.group(1)
        doc_id = doc_match.group(2)
        LOGGER.debug(f"Type: {doc_type}, ID: {doc_id}")
        dl_types = preference[doc_type]
        dl_urls = [
            (
                dl_type,
                (
                    f"{docs}/{doc_type}/d/{doc_id}/export/{dl_type}"
                    f"?id={doc_id}"
                ),
            )
            if doc_type == "presentation"
            else (
                dl_type,
                (
                    f"{docs}/{doc_type}/d/{doc_id}/export?"
                    f"format={dl_type}&id={doc_id}"
                ),
            )
            for dl_type in dl_types
        ]
        return dl_urls, default_idx

    archive = "https://archive.org"
    archive_pattern = rf"{archive}/(details|download)/([^\/]*).*"
    archive_match = re.match(archive_pattern, url)
    if archive_match:
        LOGGER.debug("Archive.org pattern matched.")
        content_name = archive_match.group(2)
        archive_url = f"{archive}/download/{content_name}"
        dl_url = f"{archive}/compress/{content_name}"
        dl_urls = [("all", dl_url)]
        default_idx = 0

        r = requests.get(archive_url)
        soup = BeautifulSoup(r.content, "html.parser")
        div = soup.find("div", class_="download-directory-listing")
        urls = div.find_all("a")
        dl_urls += [
            (
                url["href"].split(".")[-1],
                f"{archive}/download/{content_name}/{url['href']}",
            )
            for url in urls
            if (
                not url["href"].endswith(content_name)
                and not url["href"].endswith("/")
                and url.get_text().find("View Contents") == -1
            )
        ]
        preference_order = ["pdf", "mp3", "all"]
        for preference in preference_order:
            for idx, (tag, url) in enumerate(dl_urls):
                if tag == preference:
                    default_idx = idx
                    break
            else:
                continue
            break

        return dl_urls, default_idx

    dropbox_pattern = "dropbox.com"
    dropbox_match = dropbox_pattern in url
    if dropbox_match:
        parse_result = urlparse(url)
        query = dict(
            p.split("=") for p in parse_result.query.split("&") if "=" in p
        )
        query["dl"] = 1
        query_string = "&".join([f"{k}={v}" for k, v in query.items()])
        parse_result = parse_result._replace(query=query_string)
        return [("dropbox", urlunparse(parse_result))], default_idx

    LOGGER.debug("No specific pattern matched.")
    return [("direct", url)], default_idx
