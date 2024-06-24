#!/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
import signal
import time

def start_capture():
    """
    Starting capturing network traffic using tcpdump.
    """
    subprocess.Popen(["tcpdump", "-U", "-s0", "-i", "client-eth0", "src", "port", "1935", "-w", "pcap/client.pcap"])

def stop_capture():
    """
    Stopping the tcpdump process gracefully by sending a SIGINT signal.
    """
    ps_output = subprocess.check_output(['ps', '-e']).decode('utf-8')
    for line in ps_output.splitlines():
        if 'tcpdump' in line:
            pid = int(line.split()[0])
            os.kill(pid, signal.SIGINT)
            break

def get_video_stream():
    """
    Main function to handle video streaming.
    """
    out_file = "stream_output.flv"
    capture_traffic = True

    if capture_traffic:
        start_capture() # Starting to capture traffic
        time.sleep(2)

    start_time = time.time()
    ffmpeg_command = [
        "ffmpeg", "-loglevel", "info", "-stats", "-i", "rtmp://10.0.0.1:1935/live/video.flv",
        "-t", "10", "-probesize", "80000", "-analyzeduration", "15", "-c:a", "copy", "-c:v", "copy", out_file
    ]
    subprocess.run(ffmpeg_command)

    if capture_traffic:
        stop_capture() # Stopping the capturing



if __name__ == "__main__":
    get_video_stream()
