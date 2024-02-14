#!/usr/bin/env python
#
# Copyright 2024 CampaignTrip
# Copyright 2024 David Goodman
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Python client library for the Convert.com API

This client library is designed to support the Convert.com CRO testing
tool's REST API. Read more about this library at
https://github.com/CampaignTrip/convertapi-python
r

TODO: Make this into an actual client (object-oriented).
~~~~~~
"""

#from . import

import json
import logging
import traceback

import hmac
import hashlib
import binascii

from datetime import datetime, timedelta
import time

import requests
from urllib.parse import urlencode


logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s::%(funcName)s(): %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger()

LIST_EXPERIENCES_URL = "https://api.convert.com/api/v2/accounts/{account_id}/projects/{project_id}/experiences"
LIST_PROJECTS_URL = "https://api.convert.com/api/v2/accounts/{account_id}/projects"
GET_EXPERIENCE_URL = "https://api.convert.com/api/v2/accounts/{account_id}/projects/{project_id}/experiences/{experience_id}"
GET_EXPERIENCE_DAILY_REPORT_URL = "https://api.convert.com/api/v2/accounts/{account_id}/projects/{project_id}/experiences/{experience_id}/daily_report"
#GET_VARIATIONS_URL = "https://api.convert.com/api/v2/accounts/{account_id}/projects/{project_id}/experiences/{experience_id}/variations/{variation_id}"

def doRequest(url, method, extra_headers, **opts):
    """Performs the actual call to Convert.com API"""
    verbose = opts.get('verbose', 0)
    getData = opts.get('get_data', False)
    headers = {'content-type': 'application/json'}
    params = opts.get('params', {})
    body = opts.get('body', "")

    if extra_headers:
        headers.update(extra_headers)

    log.debug("Making '{}' request to URL ({}) with headers: {}".format(
        method, url, headers))
    r = None
    try:
        if method == 'GET':
            r = requests.get(url, headers=headers, params=params, data=body)
        elif method == 'POST':
            r = requests.post(url, headers=headers, params=params, data=body)
        # TODO add DEL
        else:
            raise ValueError('Undefined HTTP method "{}"'.format(method))

        d = None
        if r.status_code != 204 and \
                r.headers["content-type"].strip().startswith("application/json"):
            d = r.json()

            log.debug("Response ({}): {}".format(r.status_code, d))
            if verbose > 1:
                log.debug(json.dumps(d, indent=2))

            if r.status_code >= 200 and r.status_code <= 202:
                if verbose > 1:
                    log.debug("Success!")
                return d["data"] if getData else d

        if r.status_code >= 400 and d != None:
            if d["isError"]:
                log.error("Received an error response ({}) making {} request to '{}': {}".format(
                    r.status_code, method, url, d["message"]))
            else:
                log.error("Received bad status code '{}' when making {} request to '{}': {}".format(
                    r.status_code, method, url, r.content))
        elif d == None:
            log.error("Unknown response ({}) when making {} request to url '{}': {}".format(
                r.status_code, method, url, r.content))
    except Exception as e:
        log.error("Failed to do {} request to '{}' with error: {}".format(
            method, url, e))
        log.error("Request error contet: {}".format(str(r.content)))
        log.error(traceback.format_exc())
    return False


def getAuthSignature(application_id, expires_timestamp, url, body, secret, **kwargs):
    """
    """
    verbose = kwargs.get('verbose', 0)
    signStr = "{appId}\n{expires}\n{url}\n{body}".format(
	appId=application_id, expires=expires_timestamp, url=url, body=body)

    msg = bytes(signStr, 'utf-8')
    secret = bytes(secret, 'utf-8')
    if verbose > 0:
        log.debug("Signstr: {}".format(signStr))

    signature = str(binascii.hexlify(hmac.new(
        secret, msg,
        digestmod=hashlib.sha256
    ).digest()), 'ascii')

    log.debug("Signature: \"{}\"".format(signature))
    return signature

def listExperiences(account_id, project_id, **kwargs):
    """
    """
    verbose = kwargs.get('verbose', 0)
    u = LIST_EXPERIENCES_URL.format(
        account_id=account_id,
        project_id=project_id)

    application_id = kwargs.get('application_id')
    secret = kwargs.get('secret')

    expires_datetime = datetime.now(tz=None) + timedelta(seconds=30)
    expires_timestamp = int(expires_datetime.timestamp())


    # Body params?
    body = ""
    if kwargs.get('bodyParams', False):
        body = json.dumps(kwargs.get('bodyParams'))

    s = getAuthSignature(application_id, expires_timestamp, u, body, secret, verbose=verbose)

    method = 'POST'

    opts = {
        "verbose": verbose,
        "body": body,
        "get_data": True # return the 'data' field from response data
    }

    data = doRequest(u, method, {
        "Expires": str(expires_timestamp),
        "Convert-Application-ID": application_id,
        "Authorization": "Convert-HMAC-SHA256 Signature={}".format(s)
    }, **opts)

    # TODO support pages!
    return data


def getExperience(account_id, project_id, experience_id, **kwargs):
    verbose = kwargs.get('verbose', 0)

    u = GET_EXPERIENCE_URL.format(
        account_id=account_id,
        project_id=project_id,
        experience_id=experience_id
    )

    application_id = kwargs.get('application_id')
    secret = kwargs.get('secret')

    expires_datetime = datetime.now(tz=None) + timedelta(seconds=30)
    expires_timestamp = int(expires_datetime.timestamp())

    # We want variation data to be expanded
    body = json.dumps({
        'include': ["variations"],
        'expand': ["variations"]
    })

    s = getAuthSignature(application_id, expires_timestamp, u, body, secret)
    log.debug("Signature: \"{}\"".format(s))

    method = 'GET'
    opts = {
        "verbose": verbose,
        "body": body
    }

    data = doRequest(u, method, {
        "Expires": str(expires_timestamp),
        "Convert-Application-ID": application_id,
        "Authorization": "Convert-HMAC-SHA256 Signature={}".format(s)
    }, **opts)

    return data


#def listVariations(account_id, project_id, experience_id, **kwargs):
#    https://api.convert.com/api/v2/accounts/{account_id}/projects/{project_id}/experiences/{experience_id}/variations/{variation_id}/update

def getExperienceVariantMaps(account_id, project_id, **kwargs):
    """Returns a tuple of dicts: the first is a dict of experience id/key-name pairs,
    and the second is a dict of variant keys indexed by id.
    """
    d = listExperiences(account_id, project_id,
                        bodyParams={
                            'include': ["variations"],
                            'expand': ["variations"]
                        }, **kwargs)
    if not d:
        log.error("Failed to list experiences in account/project {accountId}/{projectId}!".format(
            accountId=accountId, projectId=projectId
        ))
        return (False, False)

    eMap = {}
    vMap = {}
    for e in d:
        i = str(e['id'])
        n = e['name']
        k = e['key']

        eMap.update({i: k})

        for v in e['variations']:
            vi = str(v['id'])
            vk = v['key']

            if i not in vMap:
                vMap.update({i: {}})
            vMap[i].update({vi: vk})

    return (eMap, vMap)


def getExperienceStats(account_id, project_id, experience_id, **kwargs):
    verbose = kwargs.get('verbose', 0)

    u = GET_EXPERIENCE_URL.format(
        account_id=account_id,
        project_id=project_id,
        experience_id=experience_id
    )

    application_id = kwargs.get('application_id')
    secret = kwargs.get('secret')

    expires_datetime = datetime.now(tz=None) + timedelta(seconds=30)
    expires_timestamp = int(expires_datetime.timestamp())

    # We want variation data to be expanded
    body = json.dumps({
        'include': ["variations", "stats"],
        'expand': ["variations"]
    })

    s = getAuthSignature(application_id, expires_timestamp, u, body, secret)
    log.debug("Signature: \"{}\"".format(s))

    method = 'GET'
    opts = {
        "verbose": verbose,
        "body": body
    }

    data = doRequest(u, method, {
        "Expires": str(expires_timestamp),
        "Convert-Application-ID": application_id,
        "Authorization": "Convert-HMAC-SHA256 Signature={}".format(s)
    }, **opts)

    return data

def getExperienceReport(account_id, project_id, experience_id, **kwargs):
    verbose = kwargs.get('verbose', 0)

    u = GET_EXPERIENCE_DAILY_REPORT_URL.format(
        account_id=account_id,
        project_id=project_id,
        experience_id=experience_id
    )

    application_id = kwargs.get('application_id')
    secret = kwargs.get('secret')

    expires_datetime = datetime.now(tz=None) + timedelta(seconds=30)
    expires_timestamp = int(expires_datetime.timestamp())

    # We want variation data to be expanded
    body = ""
    """
    body = json.dumps({
        'include': ["variations", "stats"],
        'expand': ["variations"]
    })
    """

    s = getAuthSignature(application_id, expires_timestamp, u, body, secret)
    log.debug("Signature: \"{}\"".format(s))

    method = 'POST'
    opts = {
        "verbose": verbose,
        "body": body
    }

    data = doRequest(u, method, {
        "Expires": str(expires_timestamp),
        "Convert-Application-ID": application_id,
        "Authorization": "Convert-HMAC-SHA256 Signature={}".format(s)
    }, get_data=True, **opts)

    return data
