===================
requests_downloader
===================


.. image:: https://img.shields.io/pypi/v/requests_downloader.svg
        :target: https://pypi.python.org/pypi/requests_downloader

.. image:: https://img.shields.io/travis/hrishikeshrt/requests_downloader.svg
        :target: https://travis-ci.com/hrishikeshrt/requests_downloader

.. image:: https://readthedocs.org/projects/requests_downloader/badge/?version=latest
        :target: https://requests_downloader.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/hrishikeshrt/requests_downloader/shield.svg
     :target: https://pyup.io/repos/github/hrishikeshrt/requests_downloader/
     :alt: Updates



Python package to download files


* Free software: GNU General Public License v3
* Documentation: https://requests_downloader.readthedocs.io.


Features
--------

* Hassle-free download using ``requests``
* Download from Drive, Dropbox, Archive or direct URLs
* No need to specify a name for the file to be downloaded
* Command Line Interface to download
* External ``requests.Session`` object can be passed

Usage
-----

Get multiple download options (e.g. for ``archive.org`` links)::

    from requests_downloader import downloader
    download_urls, default_idx = downloader.handle_url('<url>')


Download a file::

    from requests_downloader import downloader
    downloader.download('<download_url>')


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
