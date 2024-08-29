#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import sys
import time
import threading

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

def change_bandwidth(link, new_bw):
    info(f'*** Changing bandwidth to {new_bw} Mbps\n')
    link.intf1.config(bw=new_bw)
    link.intf2.config(bw=new_bw)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video streaming application with dynamic bandwidth.')
    parser.add_argument('--autotest', dest='autotest', action='store_true', default=False,
                        help='Enables automatic testing of the topology and closes the streaming application.')
    args = parser.parse_args()

    initial_bandwidth = 10  # initial bandwidth in Mbps
    delay = 5       # delay in milliseconds
    autotest = args.autotest

    script_directory = os.path.abspath(os.path.dirname(__file__))
    shared_directory = os.path.join(script_directory, 'pcap')

    if not os.path.exists(shared_directory):
        os.makedirs(shared_directory)

    setLogLevel('info')

    net = Containernet(controller=Controller, link=TCLink, xterms=False)
    mgr = VNFManager(net)

    info('*** Add controller\n')
    net.addController('c0')

    info('*** Creating hosts\n')
    server = net.addDockerHost('server', dimage='dev_test', ip='10.0.0.1', docker_args={'hostname': 'server'})
    client = net.addDockerHost('client', dimage='dev_test', ip='10.0.0.2', docker_args={'hostname': 'client'})

    info('*** Adding switches and links\n')
    switch1 = net.addSwitch('s1')
    switch2 = net.addSwitch('s2')
    net.addLink(switch1, server)
    middle_link = net.addLink(switch1, switch2, bw=initial_bandwidth, delay=f'{delay}ms')
    net.addLink(switch2, client)

    info('\n*** Starting network\n')
    net.start()

    info("*** Client host pings the server to test for connectivity: \n")
    reply = client.cmd("ping -c 5 10.0.0.1")
    print(reply)

    streaming_server = add_streaming_container(mgr, 'streaming_server', 'server', 'streaming_server_image', shared_directory)
    streaming_client = add_streaming_container(mgr, 'streaming_client', 'client', 'streaming_client_image', shared_directory)

    server_thread = threading.Thread(target=start_server)
    client_thread = threading.Thread(target=start_client)

    server_thread.start()
    time.sleep(2)  # Give the server time to start
    client_thread.start()

    # Change bandwidth 13 times, with a delay of 120 seconds between each change
    bandwidth = initial_bandwidth
    for i in range(13):
        # Change bandwidth
        time.sleep(120)
        bandwidth += 10
        change_bandwidth(middle_link, bandwidth)

    # Wait for threads to finish
    server_thread.join()
    client_thread.join()

    if not autotest:
        CLI(net)

    mgr.removeContainer('streaming_server')
    mgr.removeContainer('streaming_client')
    net.stop()
    mgr.stop()
