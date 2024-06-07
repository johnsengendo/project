#!/bin/bash

echo "Build docker image for the service migration."
docker build -t Assignment1 --file ./Dockerfile .
docker image prune
