#!/bin/bash

python main.py 1 &
python main.py 2 &
python server.py
