#!/usr/bin/python

"""
This is designed to be run locally on iWorkflow to remove stuck ASO in
"ERROR_IN_DELETION" status. See "Remove Service" at:
https://devcentral.f5.com/wiki/iWorkflow.APIRef_cm_cloud_tenants_tenant-name_services_iapp.ashx

Usage:
    ./delete-error.py -u username -p password

"""

import json
import httplib
from base64 import b64encode
import optparse
import sys
import socket

parser = optparse.OptionParser()


# debug option for args
parser.add_option(
    '-a',
    '--address',
    dest="address",
    default="127.0.0.1",
    action="store",
    help="address of remote device"
    )

parser.add_option(
    '-d',
    '--debug',
    dest="debug",
    default=False,
    action="store_true",
    help="Print out arg values given"
    )


parser.add_option(
    '-u',
    '--user',
    dest="remUser",
    default='admin',
    action="store",
    help="Remote user name"
    )

parser.add_option(
    '-p',
    '--pass',
    dest="remPass",
    default='admin',
    action="store",
    help="Remote user name"
    )


options, remainder = parser.parse_args()


# get auth token
def get_token(user, password, address, debug=False):
    conn = httplib.HTTPSConnection(address)
    cred = user + ":" + password
    userAndPass = b64encode(cred).decode("ascii")
    url = '/mgmt/shared/authn/login'
    post_data = '{"username":"' + user + '","password":"' + password + '"}'
    headers = {
        'Authorization': 'Basic %s' % userAndPass,
        'Content-Type': 'application/json'}
    try:
        conn.request("POST", url, post_data, headers=headers)
        r1 = conn.getresponse()
        if r1.status != 200:
            print r1.status, r1.reason
            sys.exit(0)
        data = r1.read()
    except socket.error, e:
        print e
        sys.exit(0)
    except:
        raise
    conn.close()
    data_dict = json.loads(data)
    token = data_dict['token']['token']
    return token


# GET
def get(address, url, auth_token, debug=False):
    conn = httplib.HTTPSConnection(address)
    headers = {
        'X-F5-Auth-Token': auth_token, 'Content-Type': 'application/json'}
    try:
        conn.request("GET", url, headers=headers)
        r1 = conn.getresponse()
        if r1.status != 200:
            print r1.status, r1.reason
            sys.exit(0)
        data = r1.read()
    except socket.error, e:
        print e
        sys.exit(0)
    except:
        raise
    conn.close()
    data_dict = json.loads(data)
    get_data = data_dict
    return get_data


# PUT
def put(address, url, auth_token, put_data, debug=False):
    conn = httplib.HTTPSConnection(address)
    headers = {
        'X-F5-Auth-Token': auth_token, 'Content-Type': 'application/json'}
    try:
        conn.request("PUT", url, put_data, headers=headers)
        r1 = conn.getresponse()
        if r1.status != 200:
            print r1.status, r1.reason
            sys.exit(0)
        data = r1.read()
    except socket.error, e:
        print e
        sys.exit(0)
    except:
        raise
    conn.close()
    data_dict = json.loads(data)
    put_result = data_dict
    return put_result


# post
def post(address, url, auth_token, post_data, debug=False):
    conn = httplib.HTTPSConnection(address)
    headers = {
        'X-F5-Auth-Token': auth_token, 'Content-Type': 'application/json'}
    try:
        conn.request("POST", url, post_data, headers=headers)
        r1 = conn.getresponse()
        if r1.status != 200:
            print r1.status, r1.reason
            sys.exit(0)
        data = r1.read()
    except socket.error, e:
        print e
        sys.exit(0)
    except:
        raise
    conn.close()
    data_dict = json.loads(data)
    post_result = data_dict
    return post_result


# PATCH
def patch(address, url, auth_token, patch_data, debug=False):
    conn = httplib.HTTPSConnection(address)
    headers = {
        'X-F5-Auth-Token': auth_token, 'Content-Type': 'application/json'}
    try:
        conn.request("PATCH", url, patch_data, headers=headers)
        r1 = conn.getresponse()
        if r1.status != 200:
            print r1.status, r1.reason
            sys.exit(0)
        data = r1.read()
    except socket.error, e:
        print e
        sys.exit(0)
    except:
        raise
    conn.close()
    data_dict = json.loads(data)
    patch_result = data_dict
    return patch_result


def delete(address, url, auth_token, debug=False):
    conn = httplib.HTTPSConnection(address)
    headers = {
        'X-F5-Auth-Token': auth_token, 'Content-Type': 'application/json'}
    try:
        conn.request("DELETE", url, headers=headers)
        r1 = conn.getresponse()
        if r1.status != 200:
            print r1.status, r1.reason
            sys.exit(0)
        data = r1.read()
    except socket.error, e:
        print e
        sys.exit(0)
    except:
        raise
    conn.close()
    return data


if __name__ == "__main__":

    # setup vars
    user = options.remUser
    password = options.remPass
    address = options.address
    debug = options.debug

    # print arg info in debug
    if options.debug:
        print "options dict: ", options, " remainder: ", remainder

    # get auth token
    auth_token = get_token(user, password, address, debug)
    if options.debug:
        print "auth token is: ", auth_token

    # GET list of placemnts in "status": "ERROR_IN_DELETION"
    url = '/mgmt/cm/cloud/tenants/services/placements/'
    get_placements = get(address, url, auth_token, debug)
    placements_list = get_placements['items']
    for p in placements_list:
        if p['status'] == 'ERROR_IN_DELETION':
            print "Placement ", p['appName'], " in status:"
            print "status ", p['status']
            print "For L4-L7 Service:"
            print p['tenantServiceInstance']['selfLink']

            # doing a PUT on L4-L7 Service with the body of itself
            # changes placement status to ERROR_IN_PLACEMENT
            # then we can delete the L4-L7 Service
            url = p['tenantServiceInstance']['selfLink'][17:]

            # GET service json for PUT body
            service = get(address, url, auth_token, debug)

            # format of PUT body
            put_data = json.dumps(service, indent=4)

            # Do PUT on the service to change placement status
            put_stat = put(
                address, url, auth_token, put_data, debug=False)

            # delete service right after, seems to only work if done quickly
            # I could not get to work by manually doing this with curl
            # I do not know the reason for this
            print "Deleting ", p['appName'], "\n"
            delete_stat = delete(
                address, url, auth_token, debug=False)
