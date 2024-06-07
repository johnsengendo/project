#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
About: Basic example of service (running inside a APPContainer) migration.
"""

import os
import shlex
import time

from subprocess import check_output

from comnetsemu.cli import CLI
from comnetsemu.net import Containernet, VNFManager
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.node import Controller


def get_ofport(ifce: str):
    """Get the openflow port based on the interface name.

    :param ifce (str): Name of the interface.
    """
    return (
        check_output(shlex.split("ovs-vsctl get Interface {} ofport".format(ifce)))
        .decode("utf-8")
        .strip()
    )


if __name__ == "__main__":

    # Only used for auto-testing.
    AUTOTEST_MODE = os.environ.get("COMNETSEMU_AUTOTEST_MODE", 0)

    setLogLevel("info")

    net = Containernet(controller=Controller, link=TCLink, xterms=False)
    mgr = VNFManager(net)

    info("*** Add the default controller\n")
    net.addController("c0")

    info("*** Creating the client and hosts\n")
    h1 = net.addDockerHost(
        "h1", dimage="dev_test", ip="10.0.0.11/24", docker_args={"hostname": "h1"}
    )

    h2 = net.addDockerHost(
        "h2",
        dimage="dev_test",
        ip="10.0.0.12/24",
        docker_args={"hostname": "h2", "pid_mode": "host"},
    )

    info("*** Adding switch and links\n")
    s1 = net.addSwitch("s1")
    net.addLinkNamedIfce(s1, h1, bw=1000, delay="5ms")
    net.addLinkNamedIfce(s1, h2, bw=1000, delay="5ms")
    net.addLink(
        s1, h2, bw=1000, delay="1ms", intfName1="s1-h2-int", intfName2="h2-s1-int"
    )

    info("*** Starting network\n")
    net.start()

    info("*** Setting up container services\n")
    counter_server_h2 = mgr.addContainer(
        "counter_server_h2",
        "h2",
        "service_migration",
        "python /home/server.py h2",
    )

    client_app = mgr.addContainer(
        "client_app",
        "h1",
        "service_migration",
        "python /home/client.py h1 --target_ip 10.0.0.12",
    )

    info("*** Getting the openflow port number\n")
    s1_h1_port_num = get_ofport("s1-h1")
    s1_h2_port_num = get_ofport("s1-h2")

    info("*** Adding flow rules to switch s1\n")
    check_output(
        shlex.split(
            'ovs-ofctl add-flow s1 "in_port={}, actions=output:{}"'.format(
                s1_h1_port_num, s1_h2_port_num
            )
        )
    )

    info("*** Current log of the client: \n")
    client_log = client_app.getLogs()
    print(client_log)

    def stop_service():
        info("*** Stopping the counter server on h2\n")
        try:
            mgr.removeContainer("counter_server_h2")
        except Exception as e:
            print(e)
        finally:
            net.stop()
            mgr.stop()

    if not AUTOTEST_MODE:
        CLI(net)

    while True:
        command = input("Type 'exit' to stop the server: ")
        if command.strip().lower() == "exit":
            stop_service()
            break
