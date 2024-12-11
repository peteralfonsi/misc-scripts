import subprocess
import sys

ips = { 
    # Aug instances
    "C":"18.188.233.130",
    "D":"3.15.213.145",
    "E":"3.145.175.62",
    "F":"18.224.59.243",
    "G":"3.144.242.113",
    "H":"3.15.5.203",

    # Nov instances
    "I":"3.21.34.71", 
    "J":"18.216.37.86",
    "K":"3.22.170.147",
    "L":"18.188.60.113",

    # Dec instances
    "M":"18.189.195.74",
    "N":"18.117.232.66",
    "O":"3.21.43.14",
    "P":"18.224.172.152",

    "W":"18.223.126.93", # NovCaffeine1
    "X":"18.188.23.5", # NovCaffeine2
    "Y":"52.14.196.41", # NovCaffeine3
    "Z":"18.221.251.122" # NovCaffeine4
}

plugin = None
version = "3.0.0"
if len(sys.argv) > 2:
    plugin = sys.argv[2]
instances_to_use = sys.argv[1]

version = "3.0.0"
opensearch_path = "/Users/petealft/workplace/opensearch/OpenSearch"
tar_path = "distribution/archives/linux-tar/build/distributions/opensearch-min-{}-SNAPSHOT-linux-x64.tar.gz".format(version)
plugin_path = "plugins/{}/build/distributions/{}-{}-SNAPSHOT.zip".format(plugin, plugin, version)

def scp_to_instance(item, ip_str): 
    for char in ip_str: 
        cmd = "scp -i ~/Downloads/default.pem {}/{} ec2-user@{}:/tmp".format(opensearch_path, item, ips[char]).split(" ")
        subprocess.run(cmd)

if plugin: 
    scp_to_instance(plugin_path, instances_to_use)
    
scp_to_instance(tar_path, instances_to_use)