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
    parser.add_argument('--verbose',
                        help='Enable verbose output',
                        action='store_true')
    parser.add_argument('--debug',
                        help='Enable debug information',
                        action='store_true')
    args = vars(parser.parse_args())
    urls, url_idx = downloader.handle_url(args['url'])
    if len(urls) > 1:
        options = [
            f'{idx+1:>3}. | {s.upper():<8}| {u}' for idx, (s, u) in enumerate(urls)
        ]
        print('\n'.join(options))
        valid_responses = [str(i+1) for i in range(len(options))]
        while True:
            response = input(f'Please choose which file to download (default: {url_idx + 1}): ')
            if not response:
                response = url_idx
                break

            if response not in valid_responses:
                print(
                    f"Please enter a value between 1 to {len(options)}."
                )
                continue
            else:
                response = int(response) - 1
                break
    else:
        response = url_idx

    url = urls[response][1]
    downloader.download(
        url,
        download_dir=args['download_dir'],
        download_file=args['download_file'],
        download_path=args['download_path'],
        block_size=int(args['block']),
        timeout=float(args['timeout']),
        resume=args['resume'],
        show_progress=args['progress'],
        smart=False,
        checksum=args['checksum'],
        verbose=args['verbose'],
        debug=args['debug']
    )

    return 0

###############################################################################


if __name__ == "__main__":
    sys.exit(main())
