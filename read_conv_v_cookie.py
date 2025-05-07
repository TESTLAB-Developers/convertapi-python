#!/usr/bin/python

import logging
import argparse
import json
import re
from datetime import datetime

from convertcom import getCookieData

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Positional args
    parser.add_argument('cookieStr', type=str, help="raw _conv_v cookie value")
    #parser.add_argument('key', type=str, help="key value to fetch from the cookie data", default="exp", nargs='?', const=1)
    #parser.add_argument('-v', '--verbose', action='count', default=0)
    #parser.add_argument('-q', '--quiet', action='store_true')
    args = parser.parse_args()

    d = getCookieData(args.cookieStr)
    if d:
        print(json.dumps(d, indent=2))


