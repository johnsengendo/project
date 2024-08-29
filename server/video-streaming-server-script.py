#!/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import os
import time
import signal 

def start_capture():
    proc = subprocess.Popen(["tcpdump", "-U", "-s0", "-i", "server-eth0", "src", "port", "1935", "-w", "pcap/server.pcap"])
    return proc.pid

def stop_capture(pid):
    try:
        os.kill(pid, signal.SIGINT)
        print("Capture stopped successfully.")
    except OSError as e:
        print(f"Error stopping capture: {e}")

def main():
    input_file = "video/Deadpool.mp4"
    loops_number = -1  # Stream the video indefinitely
    total_duration = 15 * 120  # 15 periods of 120 seconds each
    capture_traffic = True

    if capture_traffic:
        pid = start_capture()
        time.sleep(2)

    ffmpeg_command = [
        "ffmpeg", "-loglevel", "info", "-stats", "-re", "-stream_loop", str(loops_number), "-i", input_file,
        "-t", str(total_duration), "-c:v", "copy", "-c:a", "aac", "-ar", "44100", "-ac", "1",
        "-f", "flv", "rtmp://localhost:1935/live/video.flv"
    ]

    subprocess.run(ffmpeg_command)

    if capture_traffic:
        stop_capture(pid)

if __name__ == "__main__":
    main()
