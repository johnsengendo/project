import subprocess
import os
import time
import signal
import vlc

def start_capture():
    """
    Start packet capturing on server-eth0 interface using tcpdump. Captures all packets
    on source port 1935 and writes them to a pcap file. This is used to
    capture network traffic associated with the video streaming.
    """
    subprocess.Popen(["tcpdump", "-U", "-s0", "-i", "server-eth0", "src", "port", "1935", "-w", "pcap/server.pcap"])

def stop_capture():
    """
    Stop the tcpdump process that was started by start_capture. Searches through
    the process list, identifies the tcpdump process, and sends a SIGINT signal to
    terminate it.
    """
    ps_output = subprocess.check_output(['ps', '-e']).decode('utf-8')
    for line in ps_output.splitlines():
        if 'tcpdump' in line:
            pid = int(line.split()[0])
            os.kill(pid, signal.SIGINT)
            break

def main():
    """
    Main function to handle video streaming with optional packet capture.
    """
    input_file = "videos/road_street.mp4"
    capture_traffic = True

    if capture_traffic:
        start_capture()  # Begin packet capturing
        time.sleep(2)   # Short delay to ensure capturing starts before streaming

    # Configure VLC to stream the video
    instance = vlc.Instance('--sout=#transcode{vcodec=h264,vb=2000,acodec=mpga,ab=128}:duplicate{dst=std{access=http,mux=ts,dst=:8080/stream}}')
    player = instance.media_player_new()
    media = instance.media_new(input_file)
    media.get_mrl()
    player.set_media(media)
    player.play()
    
    # Let's say you want to stream for 30 seconds
    time.sleep(10)
    player.stop()

    if capture_traffic:
        stop_capture()  # Stopping packet capturing after streaming is done

if __name__ == "__main__":
    main()
