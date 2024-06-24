#!/bin/bash

# Updating package lists
apt-get update -y

# Installing useful tools
apt-get install -y --no-install-recommends \
    bash \
    python3 \
    bash-completion \
    curl \
    iproute2 \
    iputils-ping \
    net-tools

# Installing the packages required for streaming videos and dumping traffic (plus a text editor, useful for debugging)
apt-get install -y \
    ffmpeg \
    tcpdump \
    vlc \
    nano 
pip3 install python-vlc
