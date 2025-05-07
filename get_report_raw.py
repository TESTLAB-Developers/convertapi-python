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
    parser.add_argument('accountId', type=str, help="account ID")
    parser.add_argument('projectId', type=str, help="project ID")
    parser.add_argument('experienceId', type=str, help="experience ID")

    parser.add_argument('-a', '--applicationId', type=str, help="API application ID") # default= TODO add env variable
    parser.add_argument('-s', '--secret', type=str, help="API secret key") # default= TODO add env variable
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-q', '--quiet', action='store_true')
    args = parser.parse_args()

    if args.quiet:
        log.setLevel("ERROR")
    elif args.verbose > 0:
        log.setLevel("DEBUG")
    else:
        log.setLevel("INFO")


    d = convertcom.getExperienceDailyReport(args.accountId, args.projectId, args.experienceId,
                        application_id=args.applicationId,
                        secret=args.secret,
                        verbose=args.verbose)
    if not d:
        log.error("Failed to get experience {expId} report in account/project {accountId}/{projectId}!".format(
            expId = args.experienceId,
            accountId=args.accountId,
            projectId=args.projectId
        ))
        exit(1)
    print("Daily report:")
    print(json.dumps(d, indent=2))


    d2 = convertcom.getExperienceAggregatedReport(args.accountId, args.projectId, args.experienceId,
                        application_id=args.applicationId,
                        secret=args.secret,
                        verbose=args.verbose)
    if not d2:
        log.error("Failed to get experience {expId} report in account/project {accountId}/{projectId}!".format(
            expId = args.experienceId,
            accountId=args.accountId,
            projectId=args.projectId
        ))
        exit(1)
    print("Aggregated report:")
    print(json.dumps(d2, indent=2))

