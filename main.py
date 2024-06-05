#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import sys
import time

from comnetsemu.cli import CLI
from comnetsemu.net import Containernet, VNFManager
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.node import Controller

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script for running the video streaming app.')
    parser.add_argument('--link-bw', metavar='link_bw', type=float, nargs='?', default=10,
                        help='initial bandwidth of the link connecting the two switches in the topology (the bandwidth '
                             'is defined in Mbit/s).')
    parser.add_argument('--link-delay', metavar='link_delay', type=float, nargs='?', default=10,
                        help='initial delay of the link connecting the two switches in the topology (the delay is '
                             'defined in ms).')
    args = parser.parse_args()

    # Read the command-line arguments
    bandwidth = max(args.link_bw, 0.000001)
    delay = max(args.link_delay, 0)

    # Create the directory that will be shared with the services docker containers
    script_dir = os.path.abspath(os.path.join('./', os.path.dirname(sys.argv[0])))
    shared_dir = os.path.join(script_dir, 'shared')
    os.makedirs(shared_dir, exist_ok=True)

    # Set the logging level
    setLogLevel('info')

    # Instantiate the network and the VNF manager objects
    net = Containernet(controller=Controller, link=TCLink, xterms=False)
    mgr = VNFManager(net)

    # Add the controller to the network
    info('*** Add controller\n')
    net.addController('c0')

    # Add the hosts (server and client) to the network
    info('*** Creating hosts\n')
    server = net.addDockerHost(
        'server', dimage='video_streaming_server', ip='10.0.0.1', docker_args={'hostname': 'server'}
    )
    client = net.addDockerHost(
        'client', dimage='video_streaming_client', ip='10.0.0.2', docker_args={'hostname': 'client'}
    )

    # Add switches and links to the network
    info('*** Adding switches and links\n')
    switch1 = net.addSwitch('s1')
    switch2 = net.addSwitch('s2')
    net.addLink(switch1, server)
    middle_link = net.addLink(switch1, switch2, bw=bandwidth, delay=f'{delay}ms')
    net.addLink(switch2, client)

    # Start the network
    info('\n*** Starting network\n')
    net.start()
    print()

    # Add the video streaming (server and client) services
    streaming_server = mgr.addContainer(
        'streaming_server', 'server', 'video_streaming_server', '', docker_args={
            'volumes': {
                shared_dir: {'bind': '/home/shared/', 'mode': 'rw'}
            }
        }
    )
    streaming_client = mgr.addContainer(
        'streaming_client', 'client', 'video_streaming_client', '', docker_args={
            'volumes': {
                shared_dir: {'bind': '/home/shared/', 'mode': 'rw'}
            }
        }
    )

    # Ensure Docker containers are running
    subprocess.run('docker start streaming_server', shell=True)
    subprocess.run('docker start streaming_client', shell=True)

    # Perform the video streaming and packet capture
    subprocess.run('docker exec -d streaming_server /home/stream_video.sh', shell=True)
    subprocess.run('docker exec -d streaming_client /home/get_video_stream.sh', shell=True)

    # Wait for the user to stop the program
    input("Press Enter to stop the video streaming and packet capture...")

    # Stop the video streaming and packet capture
    subprocess.run('docker exec streaming_server pkill -f stream_video.sh', shell=True)
    subprocess.run('docker exec streaming_client pkill -f get_video_stream.sh', shell=True)

    # Perform the closing operations
    mgr.removeContainer('streaming_server')
    mgr.removeContainer('streaming_client')
    net.stop()
    mgr.stop()
