#!/bin/sh
echo "waiting for flask to be up"
gunicorn main:app -w 4 --access-logfile - --threads 3 -b 0.0.0.0:5000
