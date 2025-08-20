from opensearchpy import OpenSearch
from create_rc_multiple_indices import get_random_value, get_random_string, max_value, index_prefix, get_time, get_client
import random
import time
import threading
import sys

def get_time_query(): 
    return {
            "query": {
                "range": {
                    "time": {
                        "gte": get_time(),
                        "lt": get_time()
                    }
                }
            },
            "size": 0
        }

def get_value_query(): 
    gt = get_random_value()
    lt = min(max_value, get_random_value())
    return {
            "query": {
                "range": {
                    "value": {
                        "gte": gt,
                        "lt": lt
                    }
                }
            },
            "size": 0
        }

def get_string_query(): 
    return { 
        "query": { 
            "match": { 
                "string": get_random_string()
            }
        }
    }

def get_query(): 
    query_fn = random.choice([get_time_query, get_value_query, get_string_query]) 
    return query_fn()

def search_index(client, index_name): 
    query = get_query()
    response = client.search(
        body = query,
        index = index_name,
        params={"request_cache":"true"}
    )

num_threads = 8

client = get_client() 
num_searches = int(int(sys.argv[1]) / num_threads)
num_indices = int(sys.argv[2])
print("Beginning searches")
def search():
    for i in range(num_searches):
        for j in range(num_indices):
            index_name = index_prefix+str(j)
            search_index(client, index_name) 
        if i % 1000 == 999: 
            print("Searched all indices {}/{} times".format(i+1, num_searches))


threads = []
for i in range(num_threads): 
    threads.append(threading.Thread(target=search))
    threads[i].start()