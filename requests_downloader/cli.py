#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command Line Interface
"""

###############################################################################

import sys
import argparse

from requests_downloader import downloader

###############################################################################


def main():
    """CLI for requests_downloader"""
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='Download URL')
    parser.add_argument('--download_dir',
                        help='Specify downloads directory',
                        default='')
    parser.add_argument('--download_file',
                        help='Specify filename',
                        default=None)
    parser.add_argument('--download_path',
                        help='Specify path (ignores _dir or _file arguments)',
                        default=None)
    parser.add_argument('--block',
                        help='Block size while writing the file, in bytes',
                        default=1024)
    parser.add_argument('--timeout',
                        help='Timeout in seconds',
                        default=60)
    parser.add_argument('--resume',
                        help='Try to resume the download, if supported',
                        action='store_false')
    parser.add_argument('--progress',
                        help='Show download progressbar',
                        action='store_false')
    parser.add_argument('--checksum',
                        help='Checksum to verify integrity of the download',
                        default=None)
    args = parser.parse_args()
    urls = downloader.handle_url(args['url'])
    if len(urls) > 1:
        options = [f'{"0":>3}. All']
        options.extend([
            f'{idx+1:>3}. {s} {u}' for idx, (s, u) in enumerate(urls)
        ])
        print('\n'.join(options))
        valid_responses = [str(i) for i in range(len(options))]
        while True:
            response = input('Please choose which file to download: ')
            if response not in valid_responses:
                print(
                    f"Please enter a value between 0 to {len(options)-1}."
                )
                continue
        response = int(response)
        if response > 0:
            urls = [urls[response]]

    for source, url in urls:
        downloader.download(
            url,
            download_dir=args['download_dir'],
            download_file=args['download_file'],
            download_path=args['download_path'],
            block_size=int(args['block']),
            timeout=float(args['timeout']),
            resume=args['resume'],
            show_progress=args['progress'],
            checksum=args['checksum']
        )

    return 0

###############################################################################


if __name__ == "__main__":
    sys.exit(main())
