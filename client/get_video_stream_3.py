
import subprocess
import argparse
import os
import time

def start_capture():
    subprocess.Popen(["./tcpdump_utils/start_capture_client.sh"])

def stop_capture():
    subprocess.run(["./tcpdump_utils/stop_capture.sh"])
    time.sleep(3)

def main():
    parser = argparse.ArgumentParser(description='Get and save video stream with optional capture of incoming packets.')
    parser.add_argument('-o', '--output', default='stream_output', help='Output filename for the stream (.flv) without extension')
    parser.add_argument('-d', '--disable-capture', action='store_true', help='Disable the capture of incoming packets')
    args = parser.parse_args()
    
    out_file = f"{args.output}.flv"
    capture_traffic = not args.disable_capture

    if capture_traffic:
        start_capture()
        time.sleep(2)

    start_time = time.time()
    ffmpeg_command = [
        "ffmpeg", "-loglevel", "info", "-stats", "-i", "rtmp://10.0.0.1:1935/live/video.flv",
        "-t", "10", "-probesize", "80000", "-analyzeduration", "15", "-c:a", "copy", "-c:v", "copy", out_file
    ]
    subprocess.run(ffmpeg_command)

    run_time = time.time() - start_time

    if capture_traffic:
        stop_capture()

    print(f"\nThe stream acquisition run time is {int(run_time)}s")

if __name__ == "__main__":
    main()
