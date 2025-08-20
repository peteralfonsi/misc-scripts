import requests
import time 
import sys

start = time.time()
if sys.argv[1] == "all": 
    r = requests.post("http://localhost:9200/_cache/clear?request=true")
else:
    index_number = int(sys.argv[1])
    index_name = "index" + str(index_number)
    r = requests.post("http://localhost:9200/{}/_cache/clear?request=true".format(index_name))
end = time.time() 

print("Elapsed time = {} sec".format(end - start))