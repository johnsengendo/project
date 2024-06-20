#!/usr/bin/env python3

import subprocess

def start_capture():
    subprocess.Popen(["tcpdump", "-U", "-s0", "-i", "client-eth0", "src", "port", "1935", "-w", "pcap/client_out.pcap"])

if __name__ == "__main__":
    start_capture()
