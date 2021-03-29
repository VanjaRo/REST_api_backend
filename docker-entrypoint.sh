#!/bin/sh


flask db init
flask db migrate
flask db update

python3 main.py