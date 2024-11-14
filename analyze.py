#!/usr/bin/python3

import sys
import json
import threading as th
from queue import Queue
from urllib.parse import unquote

from utils import *
from data import location, domain, body

STATIC_DIR = sys.argv[0].replace("analyze.py", "static/")
API_CONFIG = STATIC_DIR + "api.conf"
CATEGORY_F = STATIC_DIR + "categories"
PHONE_INFO = STATIC_DIR + "info.device"
OWNER_DATA = STATIC_DIR + "domain_owners.json"

queue = Queue(15)
print_lock = th.Lock()


def run(T, dataf, fasen, ip, name, testing_label, version):
    owner = parse_json(OWNER_DATA)

    prod = th.Thread(target=producer, args=(dataf,))
    prod.daemon = True
    prod.start()

    for _ in range(T):
        cons = th.Thread(target=consumer, args=(owner, fasen, ip, name, testing_label, version))
        cons.daemon = True
        cons.start()
    prod.join()
    queue.join()


def producer(dataf):
    for req in parse_pickle(dataf):
        queue.put(req)


def consumer(owner, fasen, ip, name, testing_label, version):
    while True:
        req = queue.get()
        analyze_request(req, owner, fasen, ip, name, testing_label, version)
        queue.task_done()


def analyze_request(req, owner, fasen, ip, name, testing_label, version):
    result = {}
    if req[0]:
        content = ""
        try:
            content = req[2].content.decode("utf-8")
            req[2].path = unquote(req[2].path)
            content = unquote(content)
        except:
            return
        result["device"] = ip
        result["apk"] = name
        result['version'] = version
        result["testing_label"] = testing_label
        result["data"] = body(content, PHONE_INFO, CATEGORY_F) + body(req[2].path, PHONE_INFO, CATEGORY_F)
        result["fase"] = fasen
        result["https"] = req[2].url[:5] == "https"
        result["location"] = location(req[2].host, API_CONFIG)
        result["domain"] = domain(req[1], owner)
        result["port"] = str(req[2].port)
        result["content"] = content
        result["path"] = req[2].path
        if len(result["data"]) <= 0:
            result["data"] = [("No-PII", "-")]
        with print_lock:
            print_json2(result)
        # print_csv(result)
    else:
        dom, port = "", "-"
        if isinstance(req[1], tuple):
            dom = req[1][0]
            port = req[1][1]
        else:
            dom = req[1]
        result["device"] = ip
        result["apk"] = name
        result['version'] = version
        result["testing_label"] = testing_label
        result["fase"] = fasen
        result["https"] = True
        result["location"] = location(dom, API_CONFIG)
        result["domain"] = domain(dom, owner)
        result["port"] = str(port)
        result["data"] = [("Certificate Pinning", "-")]
        result["content"] = "-"
        result["path"] = "-"
        with print_lock:
            print_json2(result)
            # print_csv(result)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage:")
        print("\tanalyze.py <log file> <phase descriptor> <ip_terminal> <apk_name> <teting_label> <version>")
        sys.exit(1)
    dataf = sys.argv[1]
    fasen = sys.argv[2]
    ip = sys.argv[3]
    name = sys.argv[4]
    testing_label = sys.argv[5]
    version = sys.argv[6]
    # with print_lock:
    #    print_head()
    run(10, dataf, fasen, ip, name, testing_label, version)