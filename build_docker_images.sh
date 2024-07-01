#!/bin/bash

echo "Building docker image for server streaming"
docker build -t video_streaming_server --file ./server/Dockerfile.server ./server

echo "Building docker image for client streaming"
docker build -t video_streaming_client --file ./client/Dockerfile.client ./client
