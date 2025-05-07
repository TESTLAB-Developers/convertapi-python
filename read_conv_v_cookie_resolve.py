#!/usr/bin/python

import logging
import argparse
import json
import re

import convertcom

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s::%(funcName)s(): %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Positional args
    parser.add_argument('cookieStr', type=str, help="raw _conv_v cookie value")
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-q', '--quiet', action='store_true')

    parser.add_argument('-r', '--resolveIds', action='store_true', help="use convert API to resolve experient/variant IDs")
    parser.add_argument('-a', '--applicationId', type=str, help="API application ID") # default= TODO add env variable
    parser.add_argument('-s', '--secret', type=str, help="API secret key") # default= TODO add env variable
    parser.add_argument('-i', '--accountId', type=str, help="account ID") # default= TODO add env variable
    parser.add_argument('-p', '--projectId', type=str, help="project ID") # default= TODO add env variable
    args = parser.parse_args()

    if args.quiet:
        log.setLevel("ERROR")
    elif args.verbose > 0:
        log.setLevel("DEBUG")
    else:
        log.setLevel("INFO")

    if args.resolveIds:
        if not args.applicationId:
            log.error("Missing required 'applicationId' argument when using --resolveIds!")
            exit(1)
        if not args.secret:
            log.error("Missing required 'secret' argument when using --resolveIds!")
            exit(1)
        if not args.accountId:
            log.error("Missing required 'accountId' argument when using --resolveIds!")
            exit(1)
        if not args.projectId:
            log.error("Missing required 'projectId' argument when using --resolveIds!")
            exit(1)


    j = convertcom.getCookieData(args.cookieStr)
    if not j:
        log.error("Failed to get JSON data from cookie str with key: {}".format(args.key))
        exit(1)

    if not args.resolveIds:
        log.info(json.dumps(j, indent=2))
    else:
        log.info("Resolving experient/variant IDs in cookie...")


        (e, v) = convertcom.getExperienceVariantMaps(
            args.accountId,
            args.projectId,
            application_id=args.applicationId,
            secret=args.secret,
            verbose=args.verbose)
        if not e:
            log.error("Failed to get experience/variant map in account/project {accountId}/{projectId}!".format(
                accountId=args.accountId, projectId=args.projectId
            ))
            exit(1)

        r = {}
        for i in j["Experiments"]:
            d = j["Experiments"][i]
            if i in e:
                k = "{} ({})".format(e[i], i)
                r[k] = {
                    "g": d["g"],
                    "v": {}
                } # copy goals
                # now do variants
                dv = str(d["v"])
                if dv in v[i]:
                    r[k]["v"] = v[i][dv]
                elif dv == "1":
                    r[k]["v"] = "*Excluded*"
                else:
                    log.warning("Could not find variant id '{}' in variant map for experience '{}'!".format(
                        dv, i))
            else:
                log.warning("Could not find experience id '{}' in experience map!".format(i))
        if r:
            j["Experiments"] = r


        print(json.dumps(j, indent=2))

