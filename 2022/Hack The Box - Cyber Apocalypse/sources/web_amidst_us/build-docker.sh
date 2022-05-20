#!/bin/bash
docker rm -f web_amidst_us
docker build --tag=web_amidst_us .
docker run -p 1337:1337 --rm --name=web_amidst_us web_amidst_us