#!/usr/bin/python3

import requests
from threading import Lock
import hashlib
from utils import parse_data
import base64

###########################################################################################################################
#                                                                                                                         #
#                                       Location                                                                          #
#                                                                                                                         #
###########################################################################################################################

# Find location of IP from remote API.

def loc_mem(mem, lock):
    def loc(ip, api_conf):
        if ip not in mem:
            with lock:
                # This check is necesary to check posible memoization of the thread that held the lock
                if ip not in mem:
                    params = parse_data(api_conf)
                    loc = requests.get("http://api.ipstack.com/{}".format(ip), params=params).json()
                    if 'country_name' in loc.keys():
                        mem[ip] = {"country": loc["country_name"], "country_code": loc["country_code"],
                                   "is_eu": loc["location"]["is_eu"]}
                    else:
                        mem[ip] = {"country": 'Unknown', "country_code": '-', "is_eu": '-'}
        return mem[ip]

    return loc


location = loc_mem({}, Lock())


###########################################################################################################################
#                                                                                                                         #
#                                       Domain                                                                            #
#                                                                                                                         #
###########################################################################################################################

# Analize a subdomain based on the information
# given by the owners list.
def domain(subdom, owners):
    dom = get_domain(subdom)
    cat_dom = domain_cat(dom, owners)
    anc = ancestry(dom, owners)
    result = {"found": len(anc) > 0, "domain": dom, "categ": cat_dom, "subdomain": subdom}
    result["ancestry"] = anc
    cat_anc = cat_ancestry(dom, owners)
    result["categ_ancestry"] = cat_anc
    return result


# Get a list of all the names of
# the ancestry of a domain.
def ancestry(dom, owners):
    return [owners[i]["owner_name"] for i in ancestry_ids(dom, owners)]


# Get "uses" categories of ancestries
def cat_ancestry(dom, owners):
    return [owners[i]["uses"] for i in ancestry_ids(dom, owners)]


# Get a list of all the ids
# of the ancestry of a domain.
def ancestry_ids(dom, owners):
    family = []
    did = domain_id(dom, owners)
    while did:
        family.append(did)
        did = owners[did]["parent_id"]
    return family


# Get the domain from a subdomain string.
def get_domain(subdom):
    dom = None
    if subdom is not None:
        subdom = subdom.split(".")
        try:
            dom = "{}.{}".format(subdom[-2], subdom[-1])
        except IndexError:
            print('unknown structure domain')
    return dom


# If domain is in owners data return its id
# or else return None.
def domain_id(dom, owners):
    for o in owners:
        if dom in o["domains"]:
            return o["id"]
    return None


def domain_cat(dom, owners):
    for o in owners:
        if dom in o["domains"]:
            return o["uses"]
    return None


###########################################################################################################################
#                                                                                                                         #
#                                       Body                                                                              #
#                                                                                                                         #
###########################################################################################################################

def body(data, info_file, cat_file):
    res = category(data, info_file)
    cat = [category(r, cat_file)[0] for r in res]
    return list(zip(res, cat))


def category(data, data_file):
    res = []
    cat = parse_data(data_file)
    for k in cat:
        tmp = [k for e in cat[k] if e.lower() in data.lower() or
               hashlib.md5(e.encode('utf-8')).hexdigest() in data.lower() or
               hashlib.sha1(e.encode('utf-8')).hexdigest() in data.lower() or
               hashlib.sha256(e.encode('utf-8')).hexdigest() in data.lower() or
               base64.b64encode(e.encode('utf-8')).decode('utf-8') in data
               ]
        res.extend(tmp)
    return res
