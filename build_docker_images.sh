#!/bin/bash

echo "Build docker image for the video streaming server"
docker build -t video_streaming_server --file ./server/Dockerfile.server ./server

echo "Build docker image for the video streaming client"
docker build -t video_streaming_client --file ./client/Dockerfile.client ./client
