from opensearchpy import OpenSearch, helpers
import opensearchpy
import requests 
import json
import random 
import datetime
import sys

# Goal: Search against indices with lots of garbage text data so we fill the FD cache. 

client = OpenSearch(
    hosts = [{'host': "localhost", 'port': 9200}],
    http_compress = True, # enables gzip compression for request bodies
    http_auth = ("admin", "admin"),
    use_ssl = False,
    verify_certs = False,
    ssl_assert_hostname = False,
    ssl_show_warn = False
)

num_indices = int(sys.argv[1]) # usually 50
num_fields_per_index = int(sys.argv[2]) # usually 999

def search(client, index_name, field_name): 
    query = {
        "query": {
            "match_all":{}
        },
        "sort":[{field_name:{"order":"asc"}}]
    }
    response = client.search(
        body=query,
        index=index_name
    )

for i in range(num_indices): 
    index_name = "index" + str(i)
    for j in range(num_fields_per_index): 
        field_name = "text" + str(j)
        search(client, index_name, field_name)
        if j % 10 == 9: 
            print("Finished searching for field {}/{} on index {}/{}".format(j+1, num_fields_per_index, i+1, num_indices))