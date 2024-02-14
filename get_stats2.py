#!/usr/bin/python

import logging
import argparse
import json
import re

import convertcom

logging.basicConfig(
    #format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s::%(funcName)s(): %(message)s',
    format='%(asctime)s: %(message)s',
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


    e = convertcom.getExperienceStats(args.accountId, args.projectId, args.experienceId,
                        application_id=args.applicationId,
                        secret=args.secret,
                        verbose=args.verbose)
    if not e:
        log.error("Failed to get experience {expId} in account/project {accountId}/{projectId}!".format(
            expId = args.experience_id,
            accountId=args.accountId,
            projectId=args.projectId
        ))
        exit(1)
    #print(json.dumps(d, indent=2))


    r = convertcom.getExperienceReport(args.accountId, args.projectId, args.experienceId,
                        application_id=args.applicationId,
                        secret=args.secret,
                        verbose=args.verbose)
    if not r:
        log.error("Failed to get experience {expId} report in account/project {accountId}/{projectId}!".format(
            expId = args.experienceId,
            accountId=args.accountId,
            projectId=args.projectId
        ))
        exit(1)
    #print(json.dumps(d, indent=2))


    totalConversions = e["stats"]["conversions"]

    varKeyById = {}
    varSplits = ""

    for v in r["variations_data"]:
        varKeyById[v["id"]] = v["key"]

        varSplits += ("/" if len(varSplits) > 0 else "") + str(int(v["traffic_distribution"]))

    varConvById = {}
    for v in r["reportData"]["variations"]:
        varConvById[v["id"]] = v["stats"][-1]["totals"]

    varStr = ""
    for i,k in varKeyById.items():
        varStr += "\n - {k}: {c} conversions".format(k=k, c=varConvById[i])

    varWinners = []
    varWinStr = ""
    for v in e["stats"]["variations_observed_results"]:
        if v["test_result"] == "winner":
            varWinners += v
            varWinStr += "\n - {name}: improved by {percent}%".format(
                name=v["variation_name"],
                percent=round(v["improvement"] * 100, 2)
            )

    log.info("Fetched conversion and variation stats for experiment: {}".format(e["name"]))
    log.info("Recorded {total} conversions across {count} variations with split: {split}{varStr}".format(
        total=totalConversions, count=len(varKeyById), split=varSplits,
        varStr = varStr))
    log.info("Possible {count} winners across {totalCount} variations: {varWinStr}".format(
        count=len(varWinners),
        totalCount=len(varKeyById),
        varWinStr=varWinStr))


