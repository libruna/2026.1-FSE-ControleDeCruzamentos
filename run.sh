#!/bin/bash

python src/main.py 1 &
python src/main.py 2 &
python src/server.py
