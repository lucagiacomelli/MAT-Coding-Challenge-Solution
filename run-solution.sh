#!/bin/sh
# run-solution.sh

pip3 install -r requirements.txt

docker-compose up -d

until nc -z localhost 1883; do
    sleep 1 # wait before check again
done

exec python3 data_processor.py