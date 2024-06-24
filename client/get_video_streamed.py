#!/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
import signal
import time
import vlc

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
        start_capture()  # Start capturing traffic
        time.sleep(2)    # Ensure capture starts before streaming begins

    # Set up VLC to receive the stream and save it to a file
    instance = vlc.Instance()
    player = instance.media_player_new()
    media = instance.media_new("rtmp://10.0.0.1:1935/live/video.flv", ":sout=#std{access=file,mux=flv,dst='%s'}" % out_file)
    media.get_mrl()
    player.set_media(media)

    # Play the media to start the receiving and saving process
    player.play()
    # Let's say we stream for 10 seconds as specified in the ffmpeg command
    time.sleep(10)
    player.stop()

    if capture_traffic:
        stop_capture()  # Stop the capturing after streaming

if __name__ == "__main__":
    get_video_stream()
