#!/bin/bash

# install general requirements 
yes | sudo yum install git python3-pip java-21-amazon-corretto
echo export JAVA_HOME=/usr/lib/jvm/java-21-amazon-corretto >> /home/ec2-user/.zshrc 
echo export JAVA_HOME=/usr/lib/jvm/java-21-amazon-corretto >> /home/ec2-user/.bashrc

# check out appropriate repos and branches 
cd /home/ec2-user
yes | rm -r osb
mkdir osb && cd osb && git clone https://github.com/peteralfonsi/opensearch-benchmark-workloads.git
# NOTE: does not check out a particular branch for osb workloads as this is benchmark-dependent! 

yes | pip install opensearch-benchmark requests opensearch-py

# install other dependencies
#yes | sudo yum install make patch gcc zlib-devel openssl-devel libffi-devel readline-devel sqlite-devel ncurses-devel xz-devel tk-devel
yes | sudo yum -y install make gcc openssl-devel bzip2-devel libffi-devel ncurses-devel sqlite-devel readline-devel zlib-devel xz-devel

# build osb 
cd /home/ec2-user/osb_core/opensearch-benchmark
make install

# delete leftover files that might be present from earlier runs 
rm jstack-outputs/*

# configure benchmark.ini to use the correct metric store 
rm /home/ec2-user/.benchmark/benchmark.ini 
mkdir -p /home/ec2-user/.benchmark
cat << 'EOF' >> /home/ec2-user/.benchmark/benchmark.ini
[meta]
config.version = 17

[system]
env.name = local

[node]
root.dir = /home/ec2-user/.benchmark/benchmarks
src.root.dir = /home/ec2-user/.benchmark/benchmarks/src

[source]
remote.repo.url = https://github.com/opensearch-project/OpenSearch.git
opensearch.src.subdir = opensearch

[benchmarks]
local.dataset.cache = /home/ec2-user/.benchmark/benchmarks/data

[results_publishing]
datastore.type = opensearch
datastore.host = search-benchmark-metrics-small-ejyt5ebfa4va5m25ckv6m2zr44.us-east-2.es.amazonaws.com
datastore.port = 443
datastore.secure = True
datastore.user = petealft
datastore.password = Password1^
datastore.ssl.verification_mode = none

[workloads]
default.url = https://github.com/opensearch-project/opensearch-benchmark-workloads

[provision_configs]
default.dir = default-provision-config

[defaults]
preserve_benchmark_candidate = false

[distributions]
release.cache = true
EOF

# unpack opensearch .tar 
mv /tmp/opensearch-min-2.0-SNAPSHOT-linux-x64.tar.gz /home/ec2-user
cd /home/ec2-user/
tar -zxvf opensearch-min-3.2.0-SNAPSHOT-linux-x64.tar.gz

# set vmmaps to minimum value 
echo vm.max_map_count = 262144 | sudo tee -a /etc/sysctl.conf > /dev/null
sudo sysctl --system

mkdir /home/ec2-user/cluster_resource_usages