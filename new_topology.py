#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import time

from comnetsemu.cli import CLI
from comnetsemu.net import Containernet, VNFManager
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.node import Controller

def add_streaming_container(manager, name, role, image, shared_dir):
    return manager.addContainer(
        name, role, image, '', docker_args={
            'volumes': {
                shared_dir: {'bind': '/home/pcap/', 'mode': 'rw'}
            }
        }
    )

def start_server():
    subprocess.run(['docker', 'exec', '-it', 'streaming_server', 'bash', '-c', 
                    'cd /home && python3 video_server.py'])

def start_client():
    subprocess.run(['docker', 'exec', '-it', 'streaming_client', 'bash', '-c', 
                    'cd /home && python3 video_client.py'])

def main():
    net = Containernet(controller=Controller)
    
    info('*** Adding controller\n')
    net.addController('c0')
    
    info('*** Adding hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    
    info('*** Adding streaming containers\n')
    manager = VNFManager(net)
    
    server = add_streaming_container(manager, 'streaming_server', 'server', 'ubuntu', '/path/to/shared_dir')
    client = add_streaming_container(manager, 'streaming_client', 'client', 'ubuntu', '/path/to/shared_dir')
    
    info('*** Adding links\n')
    net.addLink(h1, server, cls=TCLink, bw=10)
    net.addLink(h2, client, cls=TCLink, bw=10)
    
    info('*** Starting network\n')
    net.start()
    
    info('*** Starting server and client\n')
    start_server()
    start_client()
    
    info('*** Running CLI\n')
    CLI(net)
    
    info('*** Stopping network\n')
    net.stop()

if __name__ == "__main__":
    setLogLevel('info')
    main()