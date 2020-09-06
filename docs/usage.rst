=====
Usage
=====

Get multiple download options (e.g. for ``archive.org`` links)::
    from requests_downloader import downloader
    download_urls, default_idx = downloader.handle_url('<url>')

Download a file::
    from requests_downloader import downloader
    downloader.download('<download_url>')
