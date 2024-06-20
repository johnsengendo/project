#!/env python3

import subprocess

def start_capture():
    subprocess.Popen(["tcpdump", "-U", "-s0", "-i", "server-eth0", "src", "port", "1935", "-w", "shared/server_out.pcap"])

if __name__ == "__main__":
    start_capture()
