import argparse
import subprocess
import time

def usage():
    print("Usage: python get_streaming.py [-o stream_output_filename] [-d]")
    print("    -o stream_output_filename = name of the (.flv) output file without extension (the default value is 'stream_output')")
    print("    -d = disable the capture of the video stream incoming packets through tcpdump (the capture is enabled by default, with output file 'shared/client_out.pcap')")

def main():
    parser = argparse.ArgumentParser(description="Get video stream with optional packet capture")
    parser.add_argument('-o', '--output', type=str, default='stream_output', help='Output file name without extension')
    parser.add_argument('-d', '--disable_capture', action='store_true', help='Disable packet capture')
    args = parser.parse_args()

    out_file = f"{args.output}.flv"
    capture_traffic = not args.disable_capture

    # Start tcpdump capture, if required
    if capture_traffic:
        subprocess.run(['./tcpdump_utils/start_capture_client.sh'])
        time.sleep(2)

    # Get the video stream and save it to the specified file
    start_time = time.time()
    ffmpeg_command = [
        'ffmpeg', '-i', 'rtmp://10.0.0.1:1935/live/video.flv',
        '-probesize', '80000', '-analyzeduration', '15',
        '-c:a', 'copy', '-c:v', 'copy', out_file
    ]
    subprocess.run(ffmpeg_command)
    run_time = int(time.time() - start_time)

    # Stop tcpdump capture, if required
    if capture_traffic:
        subprocess.run(['./tcpdump_utils/stop_capture.sh'])
        time.sleep(3)

    # Print the stream acquisition run time
    print(f"\nThe stream acquisition run time is {run_time}s")

if __name__ == "__main__":
    main()