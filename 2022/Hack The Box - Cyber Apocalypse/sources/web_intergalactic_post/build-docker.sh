#!/bin/bash
docker build -t web_intergalactic_post .
docker run  --name=web_intergalactic_post --rm -p1337:80 -it web_intergalactic_post
