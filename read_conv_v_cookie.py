#!/usr/bin/python

import logging
import argparse
import json
import re

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger()


def getJsonDataFromCookieKey(cookieStr, key):
    parts = cookieStr.split("*")

    s = False
    for p in parts:
        if p.startswith(key):
            s = p
            break
    if not s:
        log.error("Couldn't find key '{}' in cookie str!".format(key))
        return False

    s = s.replace('-', ',')
    s = s.replace('.', ':')
    s = re.sub(r'([a-z0-9]+):', r'"\1":', s, flags=re.MULTILINE)

    j = json.loads("{" + s + "}")
    return j


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Positional args
    parser.add_argument('cookieStr', type=str, help="raw _conv_v cookie value")
    parser.add_argument('key', type=str, help="key value to fetch from the cookie data", default="exp")
    #parser.add_argument('-v', '--verbose', action='count', default=0)
    #parser.add_argument('-q', '--quiet', action='store_true')
    args = parser.parse_args()

    j = getJsonDataFromCookieKey(args.cookieStr, args.key)
    if j:
        print(json.dumps(j, indent=2))


