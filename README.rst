===================
requests_downloader
===================


.. image:: https://img.shields.io/pypi/v/requests_downloader?color=success
        :target: https://pypi.python.org/pypi/requests_downloader

.. image:: https://readthedocs.org/projects/requests_downloader/badge/?version=latest
        :target: https://requests_downloader.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/pypi/pyversions/requests_downloader
        :target: https://pypi.python.org/pypi/requests_downloader
        :alt: Python Version Support

.. image:: https://img.shields.io/github/issues/hrishikeshrt/requests_downloader
        :target: https://github.com/hrishikeshrt/requests_downloader/issues
        :alt: GitHub Issues

.. image:: https://img.shields.io/github/followers/hrishikeshrt?style=social
        :target: https://github.com/hrishikeshrt
        :alt: GitHub Followers

.. image:: https://img.shields.io/twitter/follow/hrishikeshrt?style=social
        :target: https://twitter.com/hrishikeshrt
        :alt: Twitter Followers


Python package to download files


* Free software: GNU General Public License v3
* Documentation: https://requests_downloader.readthedocs.io.


Features
========

* Hassle-free download using ``requests``
* Download from Drive, Dropbox, Archive or direct URLs
* No need to specify a name for the file to be downloaded
* Command Line Interface to download
* External ``requests.Session`` object can be passed

Usage
=====

Use in a Project
----------------

Get multiple download options (e.g. for ``archive.org`` links):

.. code-block:: python

    from requests_downloader import downloader
    download_urls, default_idx = downloader.handle_url('<url>')


Download a file:

.. code-block:: python

    from requests_downloader import downloader
    downloader.download('<download_url>')

Use Console Interface
---------------------

.. code-block:: console

    usage: smart-dl [-h] [--download_dir DOWNLOAD_DIR] [--download_file DOWNLOAD_FILE]
                    [--download_path DOWNLOAD_PATH] [--block BLOCK] [--timeout TIMEOUT]
                    [--resume] [--progress] [--checksum CHECKSUM] [--verbose] [--debug]
                    [--version] url

    positional arguments:
    url                   Download URL

    optional arguments:
    -h, --help            show this help message and exit
    --download_dir DOWNLOAD_DIR
                            Specify downloads directory
    --download_file DOWNLOAD_FILE
                            Specify filename
    --download_path DOWNLOAD_PATH
                            Specify path (ignores _dir or _file arguments)
    --block BLOCK         Block size while writing the file, in bytes
    --timeout TIMEOUT     Timeout in seconds
    --resume              Try to resume the download, if supported
    --progress            Show download progressbar
    --checksum CHECKSUM   Checksum to verify integrity of the download
    --verbose             Enable verbose output
    --debug               Enable debug information
    --version             show program's version number and exit


Credits
=======

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
