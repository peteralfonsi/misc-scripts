from opensearchpy import OpenSearch, helpers
import random 
import sys

# Goal: Create many indices with text fields so that we can fill FD cache with various crap. 

client = OpenSearch(
    hosts = [{'host': "localhost", 'port': 9200}],
    http_compress = True, # enables gzip compression for request bodies
    http_auth = ("admin", "admin"),
    use_ssl = False,
    verify_certs = False,
    ssl_assert_hostname = False,
    ssl_show_warn = False
)
field_name_prefix = "text"
fields_per_index = 999
words_per_field = 500
words_per_document = 1
docs_per_index = 2_000
num_indices = 50


alphabet = "abcdefghijklmnopqrstuvwxyz"
word_len = 8

def create_index(client, name, do_delete_indices, enable_rc): 
    if do_delete_indices: 
        if client.indices.exists(index=name): 
            client.indices.delete(index=name)
            print("Deleting index " + name)
    body = {
        "mappings": {
            "properties": {
            "request": {"type": "text", "fielddata":"true"},
            }
        },
        "settings": { 
            "index": { 
                "requests.cache.enable": enable_rc,
                "queries.cache.enabled": False
            }
        }
    }
    for i in range(fields_per_index): 
        field_name = field_name_prefix + str(i)
        body["mappings"]["properties"][field_name] = {"type":"text", "fielddata":"true"}
    return client.indices.create(name, body=body)

def generate_word_list(): 
    ret = [] 
    for i in range(words_per_field): 
        word = []
        for j in range(word_len): 
            word.append(alphabet[random.randint(0, len(alphabet)-1)])
        ret.append("".join(word))
    return ret 


def create_document(index_name, word_list): 
    source = {}
    for i in range(fields_per_index): 
        field_name = field_name_prefix + str(i)
        value = []
        for j in range(words_per_document): 
            value.append(random.choice(word_list))
        source[field_name] = " ".join(value)

    return {
        "_index":index_name,
        "_source":source
    }

def setup(populate=True): 
    assert len(sys.argv) >= 4
    seed = sys.argv[1]
    random.seed(seed)
    lowest_index = int(sys.argv[2])
    highest_index = int(sys.argv[3]) # exclusive
    do_delete_indices=False
    if len(sys.argv) > 4: 
        do_delete_indices = bool(sys.argv[4])
        enable_rc = bool(sys.argv[5])
    for i in range(lowest_index, highest_index):
        index_name = "index"+str(i)
        create_index(client, index_name, do_delete_indices, enable_rc)

        bulk_batch_size = 2_000
        words = generate_word_list() 

        if populate:
            for batch_i in range(int(docs_per_index / bulk_batch_size)): 
                batch_docs = [] 
                for doc_i in range(bulk_batch_size): 
                    batch_docs.append(create_document(index_name, words))
                response = helpers.bulk(client, batch_docs)
                print(response)
                print("Done indexing batch {} for {}".format(batch_i, index_name))
setup()