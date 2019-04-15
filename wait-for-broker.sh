#!/bin/sh
# wait-for-broker.sh

cmd="$@"

echo "Waiting broker to launch on 1883..."

until nc -z localhost 1883; do
    echo "Broker is unavailable - sleeping"
    sleep 1 # wait before check again
done

echo "Broker is up - executing data processor"

exec $cmd