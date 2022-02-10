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
