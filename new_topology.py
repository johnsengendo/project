#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import threading
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
    middle_link = net.addLink(switch1, switch2, bw=10, delay='5ms')
    net.addLink(switch2, client)

    info('\n*** Starting network\n')
    net.start()

    info("*** Client host pings the server to test for connectivity: \n")
    reply = client.cmd("ping -c 5 10.0.0.1")
    print(reply)

    # Add containers
    streaming_server = add_streaming_container(mgr, 'streaming_server', 'server', 'streaming_server_image', shared_directory)
    streaming_client = add_streaming_container(mgr, 'streaming_client', 'client', 'streaming_client_image', shared_directory)

    # Define bandwidth and delay settings
    link_configs = [
        {'bw': 10, 'delay': '5ms'},
        {'bw': 8, 'delay': '6ms'}
    ]

    for idx, config in enumerate(link_configs):
        info(f"*** Starting streaming iteration {idx+1} with bandwidth {config['bw']} Mbps and delay {config['delay']}\n")

        # Configure the middle link with current settings
        middle_link.intf1.config(bw=config['bw'], delay=config['delay'])
        middle_link.intf2.config(bw=config['bw'], delay=config['delay'])

        # Start server and client threads
        server_thread = threading.Thread(target=start_server)
        client_thread = threading.Thread(target=start_client)

        info(f"*** Streaming with bandwidth {config['bw']} Mbps and delay {config['delay']}\n")
        server_thread.start()
        client_thread.start()

        # Wait for the streaming to complete
        server_thread.join()
        client_thread.join()

        # Capture packets and wait a bit before the next iteration
        info("*** Sleeping before next configuration...\n")
        time.sleep(5)

    if not args.autotest:
        CLI(net)

    mgr.removeContainer('streaming_server')
    mgr.removeContainer('streaming_client')
    net.stop()
    mgr.stop()
