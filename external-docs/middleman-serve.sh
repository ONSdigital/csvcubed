#!/bin/bash

docker build -t middleman . || exit 1
docker run -it --rm -v $(pwd):/workspace -w /workspace -p 4567:4567 middleman sh -c 'bundle install && bundle exec middleman serve'
