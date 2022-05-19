#!/bin/bash

# A script to build a single `shapes.ttl` files from the shapes defined in many JSON files.

riot --syntax json-ld --out ttl ../deps/shacl-context.json > context.ttl || exit 1
riot --syntax json-ld --out ttl ../deps/dcat.json > dcat.ttl || exit 1
riot --syntax json-ld --out ttl ../code-list.json > code-list.ttl || exit 1

riot --output=nt context.ttl code-list.ttl dcat.ttl | grep -v "http://www.w3.org/2002/07/owl#imports" | riot --syntax nt --output ttl > shapes.ttl

rm -rf context.ttl dcat.ttl code-list.ttl

