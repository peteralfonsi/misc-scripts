
from opensearchpy import OpenSearch
import opensearchpy
import requests 
import json
import random 
import datetime

client = OpenSearch(
    hosts = [{'host': "localhost", 'port': 9200}],
    http_compress = True, # enables gzip compression for request bodies
    http_auth = ("admin", "admin"),
    use_ssl = False,
    verify_certs = False,
    ssl_assert_hostname = False,
    ssl_show_warn = False
)

def random_date(min_date=(1,1), max_date=(12,31)): 
    # in 2023
    beginning = datetime.datetime(2023, min_date[0], min_date[1])
    end = datetime.datetime(2023, max_date[0], max_date[1])
    min_timestamp = datetime.datetime.timestamp(beginning)
    max_timestamp = datetime.datetime.timestamp(end)
    timestamp = min_timestamp + random.random() * (max_timestamp - min_timestamp)
    res = datetime.datetime.fromtimestamp(timestamp)
    return res.strftime("%Y-%m-%d %H:%M:%S")

def search_range(gte, lte): 
    query = {
        "query": {
            "range": {
                "day": {
                    "gte": gte,
                    "lt": lte
                }
            }
        },
        "size": 0
    }
    response = client.search(
        body=query,
        index="jan-index",
        params={"request_cache":"true"}
    )

prev_query_ranges = []
max_stored_prev = 100000
repeat_chance = 0.5
    
for i in range(10000000): 
    
    if random.random() < repeat_chance and len(prev_query_ranges) > 0: 
        tup = random.choice(prev_query_ranges)
        gte = tup[0]
        lte = tup[1]
    else: 
        gte = random_date(min_date=(1,1), max_date=(6,30))
        lte = random_date(min_date=(7,1), max_date=(12,31))
        if len(prev_query_ranges) < max_stored_prev: 
            prev_query_ranges.append((gte, lte))
    search_range(gte, lte)
    if i % 10000 == 0:   
        print("Searched {}-th time".format(i))