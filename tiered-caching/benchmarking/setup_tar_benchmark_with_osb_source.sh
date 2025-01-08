#!/bin/bash

# install general requirements 
yes | sudo yum install git python3-pip java-11-amazon-corretto
echo export JAVA_HOME=/usr/lib/jvm/java-11-amazon-corretto >> /home/ec2-user/.zshrc 
echo export JAVA_HOME=/usr/lib/jvm/java-11-amazon-corretto >> /home/ec2-user/.bashrc

# check out appropriate repos and branches 
cd /home/ec2-user
yes | rm -r osb
mkdir osb && cd osb && git clone https://github.com/peteralfonsi/opensearch-benchmark-workloads.git
# NOTE: does not check out a particular branch for osb workloads as this is benchmark-dependent! 

cd /home/ec2-user
yes | rm -r osb_core
mkdir osb_core && cd osb_core && git clone https://github.com/peteralfonsi/opensearch-benchmark.git
cd opensearch-benchmark && git checkout non-range-randomization
cd /home/ec2-user

# uninstall pip osb installation if present 
yes | pip uninstall opensearch-benchmark

# setup to build osb from source
# install pyenv
curl https://pyenv.run | bash
cat << 'EOF' >> /home/ec2-user/.bashrc
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
EOF
source /home/ec2-user/.bashrc

# install docker
yes | sudo yum install docker
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.23.3/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

# install other dependencies
yes | sudo yum install make patch gcc zlib-devel openssl-devel libffi-devel readline-devel sqlite-devel ncurses-devel xz-devel tk-devel

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
mv /tmp/opensearch-min-3.0.0-SNAPSHOT-linux-x64.tar.gz /home/ec2-user
cd /home/ec2-user/
tar -zxvf opensearch-min-3.0.0-SNAPSHOT-linux-x64.tar.gz

# fill in default parts of the opensearch config 

rm /home/ec2-user/opensearch-3.0.0-SNAPSHOT/config/opensearch.yml
cat << 'EOF' >> /home/ec2-user/opensearch-3.0.0-SNAPSHOT/config/opensearch.yml
# ======================== OpenSearch Configuration =========================
#
# NOTE: OpenSearch comes with reasonable defaults for most settings.
#       Before you set out to tweak and tune the configuration, make sure you
#       understand what are you trying to accomplish and the consequences.
#
# The primary way of configuring a node is via this file. This template lists
# the most important settings you may want to configure for a production cluster.
#
# Please consult the documentation for further information on configuration options:
# https://www.opensearch.org
#
# ---------------------------------- Cluster -----------------------------------
#
# Use a descriptive name for your cluster:
#
#cluster.name: my-application
#
# ------------------------------------ Node ------------------------------------
#
# Use a descriptive name for the node:
#
node.name: node-1
#
# Add custom attributes to the node:
#
#node.attr.rack: r1
#
# ----------------------------------- Paths ------------------------------------
#
# Path to directory where to store the data (separate multiple locations by comma):
#
#path.data: /path/to/data
#
# Path to log files:
#
#path.logs: /path/to/logs
#
# ----------------------------------- Memory -----------------------------------
#
# Lock the memory on startup:
#
#bootstrap.memory_lock: true
#
# Make sure that the heap size is set to about half the memory available
# on the system and that the owner of the process is allowed to use this
# limit.
#
# OpenSearch performs poorly when the system is swapping the memory.
#
# ---------------------------------- Network -----------------------------------
#
# Set the bind address to a specific IP (IPv4 or IPv6):
#
network.host: 0.0.0.0
#
# Set a custom port for HTTP:
#
#http.port: 9200
#
# For more information, consult the network module documentation.
#
# --------------------------------- Discovery ----------------------------------
#
# Pass an initial list of hosts to perform discovery when this node is started:
# The default list of hosts is ["127.0.0.1", "[::1]"]
#
discovery.seed_hosts: ["127.0.0.1"]
#discovery.seed_hosts: ["host1", "host2"]
#
# Bootstrap the cluster using an initial set of cluster-manager-eligible nodes:
#
cluster.initial_cluster_manager_nodes: ["node-1"]
#
# For more information, consult the discovery and cluster formation module documentation.
#
# ---------------------------------- Gateway -----------------------------------
#
# Block initial recovery after a full cluster restart until N nodes are started:
#
#gateway.recover_after_nodes: 3
#
# For more information, consult the gateway module documentation.
#
# ---------------------------------- Various -----------------------------------
#
# Require explicit names when deleting indices:
#
#action.destructive_requires_name: true
#
# ---------------------------------- Remote Store -----------------------------------
# Controls whether cluster imposes index creation only with remote store enabled
# cluster.remote_store.enabled: true
#
# Repository to use for segment upload while enforcing remote store for an index
# node.attr.remote_store.segment.repository: my-repo-1
#
# Repository to use for translog upload while enforcing remote store for an index
# node.attr.remote_store.translog.repository: my-repo-1
#
# ---------------------------------- Experimental Features -----------------------------------
# Gates the visibility of the experimental segment replication features until they are production ready.
#
#opensearch.experimental.feature.segment_replication_experimental.enabled: false
#
# Gates the functionality of a new parameter to the snapshot restore API
# that allows for creation of a new index type that searches a snapshot
# directly in a remote repository without restoring all index data to disk
# ahead of time.
#
#opensearch.experimental.feature.searchable_snapshot.enabled: false
#
#
# Gates the functionality of enabling extensions to work with OpenSearch.
# This feature enables applications to extend features of OpenSearch outside of
# the core.
#
#opensearch.experimental.feature.extensions.enabled: false
#
#
# Gates the optimization of datetime formatters caching along with change in default datetime formatter
# Once there is no observed impact on performance, this feature flag can be removed.
#
#opensearch.experimental.optimization.datetime_formatter_caching.enabled: false
#
# Gates the functionality of enabling Opensearch to use pluggable caches with respective store names via setting.
#
#opensearch.experimental.feature.pluggable.caching.enabled: false
#
# Gates the functionality of star tree index, which improves the performance of search aggregations.
#
#opensearch.experimental.feature.composite_index.star_tree.enabled: true
EOF

# set vmmaps to minimum value 
echo vm.max_map_count = 262144 | sudo tee -a /etc/sysctl.conf > /dev/null
sudo sysctl --system

mkdir /home/ec2-user/cluster_resource_usages
