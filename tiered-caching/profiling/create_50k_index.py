from opensearchpy import OpenSearch
import opensearchpy
import requests 
import json
import random 
import datetime

# Goal: Have one alias "indices-alias" pointing to 2 indices. 
# The indices have 1 doc each. The doc has a field "day" which is datetime.
# Index 1 ("jan-index") has a document with 1/1, index 2 ("feb-index") has one with 2/1. 

# https://opensearch.org/docs/latest/clients/python-low-level/
client = OpenSearch(
    hosts = [{'host': "localhost", 'port': 9200}],
    http_compress = True, # enables gzip compression for request bodies
    http_auth = ("admin", "admin"),
    use_ssl = False,
    verify_certs = False,
    ssl_assert_hostname = False,
    ssl_show_warn = False
)
alias_name = "indices-alias"

def create_index(client, name): 
    body = {
        "mappings": {
            "properties": {
            "day":    { "type" : "date", "format":"yyyy-MM-dd HH:mm:ss" } # changed from "date"
            }
        }
    }
    return client.indices.create(name, body=body)

def random_date(min_date=(1,1), max_date=(12,31)): 
    # in 2023
    beginning = datetime.datetime(2023, min_date[0], min_date[1])
    end = datetime.datetime(2023, max_date[0], max_date[1])
    min_timestamp = datetime.datetime.timestamp(beginning)
    max_timestamp = datetime.datetime.timestamp(end)
    timestamp = min_timestamp + random.random() * (max_timestamp - min_timestamp)
    res = datetime.datetime.fromtimestamp(timestamp)
    return res.strftime("%Y-%m-%d %H:%M:%S")

def setup(): 
    create_index(client, "jan-index")
    jan_document = { 
        "text":"Sample text for january document",
        "day":"2023-01-01 14:14:14",
        "value":23
    }
    feb_document = { 
        "text":"Sample text for february document",
        "day":"2023-02-01",
        "value":2
    }
    client.index(index="jan-index", body=jan_document, id="1", refresh=True)
    #client.index(index="feb-index", body=feb_document, id="1", refresh=True)
    # make aliases? doesnt seem to be in python package 

    # set up 50k docs for profiling use 
    num_docs = 23000
    for i in range(2, num_docs): 
        new_doc = {
            "text":"hello hello {}".format(i),
            "day":random_date(),
            "value":random.randint(0, 50)
        }
        client.index(index="jan-index", body=new_doc, id=str(i), refresh=True)
        if i % 500 == 0: 
            print("Indexed doc {}/{}".format(i, num_docs))

    '''alias_body = {
    "actions": [
        {
        "add": {
            "index": "*-index",
            "alias": alias_name
        }
        }
    ]
    } # Fixed, the wildcard makes it work
    alias_headers = {"Content-Type":"application/json"}
    requests.post("http://localhost:9200/_aliases", headers=alias_headers, data=json.dumps(alias_body))'''

def clear_caches(): 
    requests.post("http://localhost:9200/_cache/clear")

def search(max_day, year):
    print("Searching with max day = {}".format(max_day))
    query = {
        "query": {
            "range": {
                "day": {
                    "gte": "2023-01-01".format(year),
                    "lt": "{}-01-{}".format(year, str(max_day).zfill(2))
                }
            }
        },
        "size": 0
    }
    response = client.search(
        body = query,
        index = alias_name,
        params={"request_cache":"true"}
        #timeout=120
    )
    print(response) # should match january document

def get_cache_stats(): 
    #url = "http://localhost:9200/_stats/request_cache?pretty=true"
    url = "http://localhost:9200/_nodes/stats/indices/request_cache"
    #url = "http://localhost:9200/jan-index/_stats"
    response = requests.get(url)
    print(json.dumps(response.json(), indent=2))

do_setup = True
if do_setup:
    setup()
clear_caches()
