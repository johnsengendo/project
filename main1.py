#!/usr/bin/env python3
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


# check if the string represents a number
def is_number(string):
    check_ok = True
    try:
        float(string)
    except ValueError:
        check_ok = False

    return check_ok


# prompt the user for a new property value
def get_property_new_value(string_for_input, old_value):
    new_value = None
    while new_value is None or (new_value != '' and not is_number(new_value)):
        new_value = input(string_for_input)

    return float(new_value) if new_value != '' else old_value


# close the open processes
def close_open_processes(processes):
    for process in processes:
        if process.poll() is None:
            process.terminate()

    return []


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script for running the video streaming app.')
    parser.add_argument('--link-bw', metavar='link_bw', type=float, nargs='?', default=10,
                        help='initial bandwidth of the link connecting the two switches in the topology (the bandwidth '
                             'is defined in Mbit/s).')
    parser.add_argument('--link-delay', metavar='link_delay', type=float, nargs='?', default=10,
                        help='initial delay of the link connecting the two switches in the topology (the delay is '
                             'defined in ms).')
    parser.add_argument('--autotest', dest='autotest', action='store_const', const=True, default=False,
                        help='test the topology building and close the app.')
    args = parser.parse_args()

    # read the command-line arguments
    bandwidth = max(args.link_bw, 0.000001)
    delay = max(args.link_delay, 0)
    autotest = args.autotest

    # set the logging level
    setLogLevel('info')

    # instantiate the network and the VNF manager objects
    net = Containernet(controller=Controller, link=TCLink)
    mgr = VNFManager(net)

    # add the controller to the network
    info('*** Add controller\n')
    net.addController('c0')

    # add the hosts (server and client) to the network
    info('*** Creating hosts\n')
    server = net.addDockerHost(
        'server', dimage='video_streaming_server', ip='10.0.0.1', docker_args={'hostname': 'server'}
    )
    client = net.addDockerHost(
        'client', dimage='video_streaming_client', ip='10.0.0.2', docker_args={'hostname': 'client'}
    )

    # add switches and links to the network
    info('*** Adding switches and links\n')
    switch1 = net.addSwitch('s1')
    switch2 = net.addSwitch('s2')
    net.addLink(switch1, server)
    middle_link = net.addLink(switch1, switch2, bw=bandwidth, delay=f'{delay}ms')
    net.addLink(switch2, client)

    # start the network
    info('\n*** Starting network\n')
    net.start()
    print()

    # add the video streaming (server and client) services
    streaming_server = mgr.addContainer('streaming_server', 'server', 'video_streaming_server', '')
    streaming_client = mgr.addContainer('streaming_client', 'client', 'video_streaming_client', '')

    # Start tcpdump on server and client
    server_tcpdump_cmd = ['docker', 'exec', 'server', 'tcpdump', '-i', 'eth0', '-w', '/home/server_out.pcap']
    client_tcpdump_cmd = ['docker', 'exec', 'client', 'tcpdump', '-i', 'eth0', '-w', '/home/client_out.pcap']
    server_tcpdump_process = subprocess.Popen(server_tcpdump_cmd)
    client_tcpdump_process = subprocess.Popen(client_tcpdump_cmd)

    time.sleep(2)  # give tcpdump time to start

    # Start video streaming server and client using .sh scripts
    server_cmd = ['docker', 'exec', 'server', 'bash', '-c', 'cd /home && ./stream_video.sh']
    client_cmd = ['docker', 'exec', 'client', 'bash', '-c', 'cd /home && ./get_video_stream.sh']
    server_process = subprocess.Popen(server_cmd)
    client_process = subprocess.Popen(client_cmd)

    # if it is an auto-test execution, skip the interactive part
    if not autotest:
        # let the user choose the next operation
        choice = ''
        while choice != 'q':
            print('-' * 80 + '\n')
            print('Select the next operation:')
            print('1) change the middle link properties (bandwidth and delay)')
            print('2) open Mininet CLI')
            print('q) stop streaming and exit\n')
            choice = input('Enter your choice: ')
            print('')

            if choice == '1':
                # get the new values for bandwidth and delay
                bandwidth = max(get_property_new_value(
                    'New bandwidth for the link (the UM is Mbit/s, leave blank to not change it): ', bandwidth
                ), 0.000001)
                delay = max(get_property_new_value(
                    'New delay for the link (the UM is ms, leave blank to not change it): ', delay
                ), 0)

                # set the link properties accordingly
                middle_link.intf1.config(bw=bandwidth, delay=f'{delay}ms')
                middle_link.intf2.config(bw=bandwidth, delay=f'{delay}ms')
                print('\n')
            elif choice == '2':
                # open mininet CLI
                CLI(net)
                print()
            elif choice == 'q':
                print('Stopping streaming and exiting...')
                server_process.terminate()
                client_process.terminate()
                server_tcpdump_process.terminate()
                client_tcpdump_process.terminate()
                break
            else:
                print('Unknown choice: \'{}\''.format(choice))

    # perform the closing operations
    mgr.removeContainer('streaming_server')
    mgr.removeContainer('streaming_client')
    net.stop()
    mgr.stop()
