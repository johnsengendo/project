#!/bin/bash

echo "Building docker image for server streaming"
docker build -t streaming_server_image --file ./server/Dockerfile.server ./server

echo "Building docker image for client streaming"
docker build -t streaming_client_image --file ./client/Dockerfile.client ./client
