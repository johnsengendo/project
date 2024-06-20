
import subprocess
import argparse
import os

def start_capture():
    subprocess.Popen(["tcpdump", "-U", "-s0", "-i", "server-eth0", "src", "port", "1935", "-w", "pcap/server_out.pcap"])

def stop_capture():
    subprocess.run(["./tcpdump_utils/stop_capture.sh"])
    subprocess.sleep(3)

def main():
    parser = argparse.ArgumentParser(description='Stream video using ffmpeg with optional capture of outgoing packets.')
    parser.add_argument('-i', '--input', default='videos/big_buck_bunny_720p_5mb.mp4', help='Input video filepath')
    parser.add_argument('-o', '--once', action='store_true', help='Stream the video once, without looping')
    parser.add_argument('-d', '--disable-capture', action='store_true', help='Disable the capture of outgoing packets')
    args = parser.parse_args()
    
    capture_traffic = not args.disable_capture
    loops_number = 0 if args.once else -1

    if capture_traffic:
        start_capture()
        subprocess.sleep(2)

    ffmpeg_command = [
        "ffmpeg", "-loglevel", "info", "-stats", "-re", "-stream_loop", str(loops_number), "-i", args.input,
        "-t", "10", "-c:v", "copy", "-c:a", "aac", "-ar", "44100", "-ac", "1",
        "-f", "flv", "rtmp://localhost:1935/live/video.flv"
    ]
    subprocess.run(ffmpeg_command)

    if capture_traffic:
        stop_capture()

if __name__ == "__main__":
    main()
