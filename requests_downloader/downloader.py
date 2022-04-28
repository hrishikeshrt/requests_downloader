#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main module containing download function
"""

###############################################################################

import os
import logging
import mimetypes
from urllib.parse import unquote

import requests
from tqdm import tqdm

from .handlers import handle_url
from .utils import md5sum

###############################################################################

LOGGER = logging.getLogger(__name__)

###############################################################################

HEADERS = {
    "Range": "bytes=0-",
    "User-Agent": (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) "
        "Gecko/20100101 Firefox/89.0"
    ),
    "Upgrade-Insecure-Requests": "1",
    "Connection": "keep-alive",
    "Keep-Alive": "timeout=10, max=100",
}

###############################################################################


def download(
    url,
    download_dir="",
    download_file=None,
    download_path=None,
    headers={},
    session=None,
    block_size=1024,
    timeout=60,
    resume=True,
    show_progress=True,
    show_progress_desc=True,
    checksum=None,
    smart=True,
    url_handler=None,
):
    """
    Download a file

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
            * This behaviour is inherited from `requests.Session()`
    session : object, optional
        A valid `requests.Session` object.
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
    show_progress_desc : str or bool, optional
        Show the description to the left of progressbar.
        If False or None, no description is shown.
        If True, the name of file being downloaded is shown.
        Otherwise, the `str()` of the provided value is shown.
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

    LOGGER.debug(f"URL: {url}")

    if session is None:
        session = requests.Session()
        session.headers.update(HEADERS)

    LOGGER.debug(session.headers)
    r = session.head(url, headers=headers, timeout=timeout)

    resume_supported = r.headers.get("accept-ranges") == "bytes"
    file_mode = "ab" if resume_supported else "wb"
    LOGGER.debug(f"Resume Supported: {resume_supported}")

    r = session.get(url, headers=headers, timeout=timeout, stream=True)
    LOGGER.debug(r.headers)

    content_length = int(r.headers.get("content-length", 0))
    LOGGER.debug(f"Content-Length: {content_length}")

    content_range = r.headers.get("content-range", "")
    _content_range_part = content_range.split("/")[-1].strip()
    LOGGER.debug(f"Content-Range: {content_range}")

    if content_length == 0 and _content_range_part:
        content_length = int(_content_range_part)
        LOGGER.debug(f"Content-Length (from Range): {content_length}")

    content_type = r.headers.get("content-type")
    html_content = content_type == "text/html; charset=utf-8"
    LOGGER.debug(f"Content-Type: {content_type}")
    LOGGER.debug(f"HTML Content: {html_content}")

    if html_content:
        LOGGER.error("HTML content detected.")
        LOGGER.error(f"Download from {url} aborted.")
        return False

    extension_guess = mimetypes.guess_extension(content_type)
    LOGGER.debug(f"Extension Guess: {extension_guess}")

    visible_name = r.url.split("/")[-1]
    if extension_guess and not visible_name.endswith(extension_guess):
        visible_name += f".{extension_guess}"
    visible_name = unquote(visible_name, "UTF-8")
    LOGGER.debug(f"Visible Name: {visible_name}")

    provided_name = None
    cd = r.headers.get("content-disposition", None)
    LOGGER.debug(f"Content-Disposition: {cd}")
    if cd is not None:
        cd_fields = {}
        for part in cd.split(";"):
            _kv = part.split("=")
            if "=" in part:
                _k = _kv[0].strip(" \t\n\"'")
                _v = _kv[1].strip(" \t\n\"'")
                cd_fields[_k] = _v

        LOGGER.debug(cd_fields)
        provided_names = [v for k, v in cd_fields.items() if k == "filename"]
        provided_encoded_names = [
            v for k, v in cd_fields.items() if k == "filename*"
        ]

        # provided_names = re.findall('filename="(.+)"', cd)
        LOGGER.debug(f"Filenames: {provided_names}")
        LOGGER.debug(f"Filenames*: {provided_encoded_names}")

        if provided_names:
            provided_name = provided_names[0]

        if provided_encoded_names:
            encoding, name = provided_encoded_names[0].split("''")
            LOGGER.debug(f"Encoding: '{encoding}', Name: '{name}'")
            provided_name = unquote(name, encoding=encoding)

        LOGGER.debug(f"Final Provided Name: {provided_name}")

    if not download_file:
        download_file = provided_name if provided_name else visible_name

    if not download_file:
        LOGGER.error("Download location could not be inferred.")
        LOGGER.error(f"Download from {url} aborted.")
        return False

    if not download_path:
        download_path = os.path.join(download_dir, download_file)
    else:
        download_file = os.path.basename(download_path)

    LOGGER.info(
        f"Downloading '{download_file}' ... " f"({content_length} bytes)"
    )

    with open(download_path, "ab") as f:
        position = f.tell()
        LOGGER.debug(f"Current Position: {position}")
        if position and position == content_length:
            LOGGER.info(f"File '{download_file}' is already downloaded!")
            return download_path

    wrote = 0
    with open(download_path, file_mode) as f:
        position = f.tell()
        if resume and resume_supported:
            if position:
                headers["Range"] = f"bytes={position}-"
                LOGGER.info(
                    f"Resuming '{download_file}' from {position} bytes"
                )

            r = session.get(url, headers=headers, timeout=timeout, stream=True)

        if show_progress_desc:
            if show_progress_desc is True:
                desc = download_file
            else:
                desc = str(show_progress_desc)
        else:
            desc = None
        with tqdm(
            initial=position,
            desc=desc,
            total=content_length,
            unit="B",
            unit_scale=True,
            disable=not show_progress,
        ) as t:
            for data in r.iter_content(block_size):
                wrote += f.write(data)
                t.update(len(data))

    LOGGER.debug(f"Wrote: {wrote}")

    if content_length == 0:
        filesize = os.stat(download_path).st_size
        LOGGER.debug(f"Filesize: {filesize}")
        if not filesize:
            os.unlink(download_path)
            LOGGER.warning(
                f"Downloaded file '{download_file}' was empty and was removed."
            )
            success = False
        else:
            LOGGER.warning(
                f"Integrity of '{download_file}' could not verified."
            )
    elif (position + wrote) != content_length:
        success = False
        LOGGER.warning(f"Inconsistency in download from '{url}'.")
        LOGGER.debug(
            f"Wrote {wrote} bytes out of {content_length - position}."
        )

    if checksum is not None:
        download_checksum = md5sum(download_path)
        if download_checksum != checksum:
            success = False
            LOGGER.warning("Invalid checksum.")
            LOGGER.debug(
                f"md5sum({download_file}) = {download_checksum} != {checksum})"
            )

    if success:
        LOGGER.info(f"Successfully downloaded '{download_file}' from '{url}'.")
        return download_path
    else:
        LOGGER.info(
            f"An error occurred in downloading '{download_file}' from '{url}'."
        )
        return False


###############################################################################
