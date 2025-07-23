from data import location, domain, body
import sys
from utils import *

import json
import csv

STATIC_DIR = "/privapp/app/analyze-master/static/"
OWNER_DATA = STATIC_DIR + "domain_owners.json"
owner = parse_json(OWNER_DATA)

#read data from csv
csvfile = open("/privapp/app/analyze-master/results2.csv", 'r')
csvfile_out = open ("/privapp/app/analyze-master/results2_out.csv", 'w')

fields = ("timestamp","json.testing_label","json.apk","json.device","json.category","json.PII","json.country","json.domain","json.fase","json.https","json.int_transfer","json.port")
fields_out = ("timestamp","json.testing_label", "json.apk","json.device","json.category","json.PII","json.country","json.domain","json.fase","json.https","json.int_transfer","json.port", "json.categ", "json.ancestry", "json.categ_ancestry")

reader =csv.DictReader(csvfile, fields)
writer = csv.DictWriter(csvfile_out, fieldnames=fields_out)
writer.writeheader()
for row in reader:
    dom = row['json.domain']
    #print(row)
    dic = {}
    dic["domain"] = domain(dom, owner)
    row["json.categ"] = dic["domain"]["categ"]
    row["json.ancestry"] = dic["domain"]["ancestry"]
    row["json.categ_ancestry"] = dic["domain"]["categ_ancestry"]
    writer.writerow(row)
