#!/bin/bash

i=1
while [ -e log/log-$i ]; do
    ((i++))
done

mv log/latest.txt log/log-$i.txt 2> /dev/null

touch log/latest.txt

script -q -c "python src/main.py 1 &  python src/main.py 2 & python src/server.py" log/latest.txt
