#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import sys
import time

from comnetsemu.cli import CLI, spawnXtermDocker
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

    # create the directory that will be shared with the services docker containers
    script_dir = os.path.abspath(os.path.join('./', os.path.dirname(sys.argv[0])))
    shared_dir = os.path.join(script_dir, 'shared')
    os.makedirs(shared_dir, exist_ok=True)

    # set the logging level
    setLogLevel('info')

    # instantiate the network and the VNF manager objects
    net = Containernet(controller=Controller, link=TCLink, xterms=False)
    mgr = VNFManager(net)

    # add the controller to the network
    info('*** Add controller\n')
    net.addController('c0')

    # add the hosts (server and client) to the network
    info('*** Creating hosts\n')
    server = net.addDockerHost(
        'server', dimage='dev_test', ip='10.0.0.1', docker_args={'hostname': 'server'}
    )
    client = net.addDockerHost(
        'client', dimage='dev_test', ip='10.0.0.2', docker_args={'hostname': 'client'}
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

    info("*** Client host pings the server: \n")
    reply = client.cmd("ping -c 5 10.0.0.1")
    print(reply)
    
    # add the video streaming (server and client) services
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

    # if it is an auto-test execution, skip the interactive part
    if not autotest:
        subprocess.run(['docker', 'exec', '-it', 'streaming_server', 'bash', '-c', 'cd /home && ./combined_server_client.sh'])
        # open a terminal on the streaming service containers (both server and client)
        #spawnXtermDocker('streaming_server')
        #spawnXtermDocker('streaming_client')

        # let the user choose the next operation
        choice = ''
        open_plot_processes = []
        while choice != 'q':
            print('-' * 80 + '\n')
            print('Select the next operation:')
            print('q) exit\n')
            choice = input('Enter your choice: ')
            print('')
            if choice != 'q':
                print('Unknown choice: \'{}\''.format(choice))


        # close processes that are still open
        close_open_processes(open_plot_processes)

    # perform the closing operations
    mgr.removeContainer('streaming_server')
    mgr.removeContainer('streaming_client')
    net.stop()
    mgr.stop()
