#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import sys
import time
import threading
import random

from comnetsemu.cli import CLI, spawnXtermDocker
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
    subprocess.run(['docker', 'exec', '-it', 'streaming_server', 'bash', '-c', 'cd /home && python3 video_streaming.py'])


def start_client():
    subprocess.run(['docker', 'exec', '-it', 'streaming_client', 'bash', '-c', 'cd /home && python3 get_video_streamed.py'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video streaming application.')
    parser.add_argument('--autotest', dest='autotest', action='store_const', const=True, default=False,
                        help='Enables automatic testing of the topology and closes the streaming application.')
    args = parser.parse_args()

    # Prepare shared folder to store the pcap files
    script_directory = os.path.abspath(os.path.dirname(__file__))
    shared_directory = os.path.join(script_directory, 'pcap')

    if not os.path.exists(shared_directory):
        os.makedirs(shared_directory)

    setLogLevel('info')

    # Create network and VNF manager
    net = Containernet(controller=Controller, link=TCLink, xterms=False)
    mgr = VNFManager(net)

    info('*** Add controller\n')
    net.addController('c0')

    info('*** Creating hosts\n')
    server = net.addDockerHost(
        'server', dimage='dev_test', ip='10.0.0.1', docker_args={'hostname': 'server'}
    )
    client = net.addDockerHost(
        'client', dimage='dev_test', ip='10.0.0.2', docker_args={'hostname': 'client'}
    )

    info('*** Adding switches and links\n')
    switch1 = net.addSwitch('s1')
    switch2 = net.addSwitch('s2')

    net.addLink(switch1, server)
    net.addLink(switch2, client)

    info('\n*** Starting network\n')
    net.start()

    info("*** Client host pings the server to test for connectivity: \n")
    reply = client.cmd("ping -c 5 10.0.0.1")
    print(reply)

    # Add containers
    streaming_server = add_streaming_container(mgr, 'streaming_server', 'server', 'streaming_server_image', shared_directory)
    streaming_client = add_streaming_container(mgr, 'streaming_client', 'client', 'streaming_client_image', shared_directory)

    # Run the streaming process 20 times with varying conditions
    for i in range(20):
        # Randomize bandwidth and delay for each run
        bandwidth = random.choice([5, 10])  # bandwidth in Mbps
        delay = random.choice([5, 10])       # delay in milliseconds

        info(f"*** Iteration {i+1}: Setting bandwidth to {bandwidth} Mbps and delay to {delay} ms\n")

        # Reconfigure the middle link with new parameters
        middle_link = net.addLink(switch1, switch2, bw=bandwidth, delay=f'{delay}ms')

        # Start server and client threads
        server_thread = threading.Thread(target=start_server)
        client_thread = threading.Thread(target=start_client)

        server_thread.start()
        client_thread.start()

        server_thread.join()
        client_thread.join()

        # Remove the middle link for the next iteration
        net.delLinkBetween(switch1, switch2)

    if not args.autotest:
        CLI(net)

    mgr.removeContainer('streaming_server')
    mgr.removeContainer('streaming_client')
    net.stop()
    mgr.stop()
