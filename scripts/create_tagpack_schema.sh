#!/bin/bash

host=localhost 
if [ -n "$1" ] ; then
    host="$1"
fi

echo "Creating Cassandra target keyspace on $host"
cqlsh "$host" -f ./scripts/schema_tagpacks.cql
