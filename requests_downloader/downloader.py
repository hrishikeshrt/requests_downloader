#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main module containing download function
"""

###############################################################################

import os
import re
import hashlib
import logging
import mimetypes
from urllib.parse import urlparse, urlunparse, unquote

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

###############################################################################

HEADERS = {
    'Range': 'bytes=0-',
    'User-Agent': ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) '
                   'Gecko/20100101 Firefox/89.0'),
    'Upgrade-Insecure-Requests': '1',
    'Connection': 'keep-alive',
    'Keep-Alive': 'timeout=10, max=100'
}

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
    drive = 'https://drive.google.com'
    drive_pattern_1 = rf'{drive}/file/d/([^\/]*)/.*'
    drive_match_1 = re.match(drive_pattern_1, url)
    if drive_match_1:
        log.debug("Google Drive pattern-1 matched.")
        file_id = drive_match_1.group(1)
        dl_url = f'{drive}/u/0/uc?id={file_id}&export=download'
        return [('drive', dl_url)], default_idx

    drive_pattern_2 = rf'{drive}/open\?id=([^\/&]*).*'
    drive_match_2 = re.match(drive_pattern_2, url)
    if drive_match_2:
        log.debug("Google Drive pattern-2 matched.")
        file_id = drive_match_2.group(1)
        dl_url = f'{drive}/u/0/uc?id={file_id}&export=download'
        return [('drive', dl_url)], default_idx

    docs = 'https://docs.google.com'
    preference = {
        'spreadsheets': ['xlsx', 'ods', 'pdf'],
        'document': ['docx', 'odt', 'pdf'],
        'presentation': ['pptx', 'odp', 'pdf']
    }
    doc_pattern = rf'{docs}/(spreadsheets|document|presentation)/d/([^\/]*)/.*'
    doc_match = re.match(doc_pattern, url)
    if doc_match:
        log.debug("Google Docs pattern matched.")
        doc_type = doc_match.group(1)
        doc_id = doc_match.group(2)
        log.debug(f"Type: {doc_type}, ID: {doc_id}")
        dl_types = preference[doc_type]
        dl_urls = [
            (dl_type, (f'{docs}/{doc_type}/d/{doc_id}/export/{dl_type}'
                       f'?id={doc_id}'))
            if doc_type == 'presentation' else
            (dl_type, (f'{docs}/{doc_type}/d/{doc_id}/export?'
                       f'format={dl_type}&id={doc_id}'))
            for dl_type in dl_types
        ]
        return dl_urls, default_idx

    archive = 'https://archive.org'
    archive_pattern = rf'{archive}/(details|download)/([^\/]*).*'
    archive_match = re.match(archive_pattern, url)
    if archive_match:
        log.debug("Archive.org pattern matched.")
        content_name = archive_match.group(2)
        archive_url = f'{archive}/download/{content_name}'
        dl_url = f'{archive}/compress/{content_name}'
        dl_urls = [('all', dl_url)]
        default_idx = 0

        r = requests.get(archive_url)
        soup = BeautifulSoup(r.content, 'html.parser')
        div = soup.find('div', class_='download-directory-listing')
        urls = div.find_all('a')
        dl_urls += [(
            url['href'].split('.')[-1],
            f"{archive}/download/{content_name}/{url['href']}"
        )
            for url in urls
            if (not url['href'].endswith(content_name) and
                not url['href'].endswith('/') and
                url.get_text().find("View Contents") == -1)
        ]
        preference_order = ['pdf', 'mp3', 'all']
        for preference in preference_order:
            for idx, (tag, url) in enumerate(dl_urls):
                if tag == preference:
                    default_idx = idx
                    break
            else:
                continue
            break

        return dl_urls, default_idx

    dropbox_pattern = 'dropbox.com'
    dropbox_match = dropbox_pattern in url
    if dropbox_match:
        parse_result = urlparse(url)
        query = dict(
            p.split('=')
            for p in parse_result.query.split('&')
            if '=' in p
        )
        query['dl'] = 1
        query_string = '&'.join([f"{k}={v}" for k, v in query.items()])
        parse_result = parse_result._replace(query=query_string)
        return [('dropbox', urlunparse(parse_result))], default_idx

    log.debug("No specific pattern matched.")
    return [('direct', url)], default_idx


def download(url, download_dir='', download_file=None, download_path=None,
             headers={}, session=None, block_size=1024, timeout=60,
             resume=True, show_progress=True, checksum=None, smart=True,
             url_handler=None, verbose=False, debug=False):
    """
    Download a file

    Using 'requests' module

    Parameters
    ----------
    url : str
        URL to download.
    download_dir : str, optional
        Path of the directory to download the file in.
        The default is '' (i.e. current directory).
    download_file : str, optional
        Name for the downloaded file.
        If None, the function will infer it from URL and Content-Disposition
        The default is None.
    download_path : str, optional
        Full path where the downloaded file should be saved.
        If None, the function will save it in `download_dir/download_file`
        If provided, `download_dir` and `download_file` arguments are ignored.
        The default is None.
    headers : dict, optional
        Headers to be sent.
        The default is {}.
        Note:
            * These headers are merged with a default set of headers.
            * In case of a conflict the user-provided values are used.
            * This behaviour is inherited from requests.Session()
    session : object, optional
        A valid requests.Session object.
        This is useful when download url requires authentication.
        In such a case, authentication can be handled independently in session.
        The default is None.
    block_size : int, optional
        Block size, in bytes, to stream the downloadable content.
        The default is 1024.
    timeout : float, optional
        Timeout, in seconds
        The default is 60.
    resume : bool, optional
        Try to resume download.
        The default is True.
    show_progress : bool, optional
        Show progressbar.
        The default is True.
    checksum : str, optional
        Value of md5 checksum of the file to be downloaded.
        If provided, the downloaded file will be verified using the checksum.
        The default is None.
    smart : bool, optional
        Use url_handler for special case URLs
        The default is True.
    url_handler : function, optional
        Handler function for special cases of download URLs
        The function should return a list of (TAG, URL) pairs and default index

    Returns
    -------
    download_path: str or None
        If download was successful, full `download_path`
        otherwise, None
    """
    success = True
    if smart:
        if url_handler is None:
            url_handler = handle_url
        urls, url_idx = url_handler(url)
        url = urls[url_idx][1]

    log.debug(f"URL: {url}")

    if session is None:
        session = requests.Session()
        session.headers.update(HEADERS)

    log.debug(session.headers)
    r = session.head(url, headers=headers, timeout=timeout)

    resume_supported = r.headers.get('accept-ranges') == 'bytes'
    file_mode = 'ab' if resume_supported else 'wb'
    log.debug(f"Resume Supported: {resume_supported}")

    r = session.get(
        url, headers=headers, timeout=timeout, stream=True
    )
    log.debug(r.headers)

    content_length = int(r.headers.get('content-length', 0))
    log.debug(f"Content-Length: {content_length}")

    content_range = r.headers.get('content-range', '')
    _content_range_part = content_range.split('/')[-1].strip()
    log.debug(f"Content-Range: {content_range}")

    if content_length == 0 and _content_range_part:
        content_length = int(_content_range_part)
        log.debug(f"Content-Length (from Range): {content_length}")

    content_type = r.headers.get('content-type')
    html_content = (content_type == 'text/html; charset=utf-8')
    log.debug(f"Content-Type: {content_type}")
    log.debug(f"HTML Content: {html_content}")

    if html_content:
        log.error("HTML content detected.")
        log.error(f"Download from {url} aborted.")
        return False

    extension_guess = mimetypes.guess_extension(content_type)
    log.debug(f"Extension Guess: {extension_guess}")

    visible_name = r.url.split('/')[-1]
    if extension_guess and not visible_name.endswith(extension_guess):
        visible_name += f'.{extension_guess}'
    visible_name = unquote(visible_name, 'UTF-8')
    log.debug(f"Visible Name: {visible_name}")

    provided_name = None
    cd = r.headers.get('content-disposition', None)
    log.debug(f"Content-Disposition: {cd}")
    if cd is not None:
        cd_fields = {}
        for part in cd.split(';'):
            _kv = part.split('=')
            if '=' in part:
                _k = _kv[0].strip(' \t\n"\'')
                _v = _kv[1].strip(' \t\n"\'')
                cd_fields[_k] = _v

        log.debug(cd_fields)
        provided_names = [
            v for k, v in cd_fields.items() if k == 'filename'
        ]
        provided_encoded_names = [
            v for k, v in cd_fields.items() if k == 'filename*'
        ]

        # provided_names = re.findall('filename="(.+)"', cd)
        log.debug(f"Filenames: {provided_names}")
        log.debug(f"Filenames*: {provided_encoded_names}")

        if provided_names:
            provided_name = provided_names[0]

        if provided_encoded_names:
            encoding, name = provided_encoded_names[0].split("''")
            log.debug(f"Encoding: '{encoding}', Name: '{name}'")
            provided_name = unquote(name, encoding=encoding)

        log.debug(f"Final Provided Name: {provided_name}")

    if not download_file:
        download_file = provided_name if provided_name else visible_name

    if not download_file:
        log.error("Download location could not be inferred.")
        log.error(f"Download from {url} aborted.")
        return False

    if not download_path:
        download_path = os.path.join(download_dir, download_file)
    else:
        download_file = os.path.basename(download_path)

    log.info(
        f"Downloading '{download_file}' ... "
        f"({content_length} bytes)"
    )

    with open(download_path, 'ab') as f:
        position = f.tell()
        log.debug(f"Current Position: {position}")
        if position and position == content_length:
            log.info(f"File '{download_file}' is already downloaded!")
            return download_path

    wrote = 0
    with open(download_path, file_mode) as f:
        position = f.tell()
        if resume and resume_supported:
            if position:
                headers['Range'] = f'bytes={position}-'
                log.info(
                    f"Resuming '{download_file}' from {position} bytes"
                )

            r = session.get(
                url, headers=headers, timeout=timeout, stream=True
            )

        with tqdm(
            initial=position,
            total=content_length,
            unit='B',
            unit_scale=True,
            disable=not show_progress
        ) as t:
            for data in r.iter_content(block_size):
                wrote += f.write(data)
                t.update(len(data))

    log.debug(f"Wrote: {wrote}")

    if content_length == 0:
        filesize = os.stat(download_path).st_size
        log.debug(f"Filesize: {filesize}")
        if not filesize:
            os.unlink(download_path)
            log.warning(
                f"Downloaded file '{download_file}' was empty and was removed."
            )
            success = False
        else:
            log.warning(f"Integrity of '{download_file}' could not verified.")
    elif (position + wrote) != content_length:
        success = False
        log.warning(f"Inconsistency in download from '{url}'.")
        log.debug(
            f"Wrote {wrote} bytes out of {content_length - position}."
        )

    if checksum is not None:
        download_checksum = md5sum(download_path)
        if download_checksum != checksum:
            success = False
            log.warning("Invalid checksum.")
            log.debug(
                f"md5sum({download_file}) = {download_checksum} != {checksum})"
            )

    if success:
        log.info(f"Successfully downloaded '{download_file}' from '{url}'.")
        return download_path
    else:
        log.info(
            f"An error occurred in downloading '{download_file}' from '{url}'."
        )
        return False

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
