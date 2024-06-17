import argparse
import subprocess
import time

def usage():
    print("Usage: python stream_video.py [-i video] [-o] [-d]")
    print("    -i video = input video filepath, with default value 'videos/big_buck_bunny_720p_5mb.mp4'")
    print("    -o = stream the video once, without looping on it (the default behaviour is an infinite loop)")
    print("    -d = disable the capture of the video stream outgoing packets through tcpdump (the capture is")
    print("                   enabled by default, with output file 'shared/server_out.pcap'")

def main():
    parser = argparse.ArgumentParser(description="Stream video with optional packet capture")
    parser.add_argument('-i', '--input', type=str, default='videos/big_buck_bunny_720p_5mb.mp4', help='Input video filepath')
    parser.add_argument('-o', '--once', action='store_true', help='Stream the video once without looping')
    parser.add_argument('-d', '--disable_capture', action='store_true', help='Disable packet capture')
    args = parser.parse_args()

    video = args.input
    loops_number = '0' if args.once else '-1'
    capture_traffic = not args.disable_capture

    # Start tcpdump capture, if required
    if capture_traffic:
        subprocess.run(['./tcpdump_utils/start_capture_server.sh'])
        time.sleep(2)

    # Stream the specified video using ffmpeg
    ffmpeg_command = [
        'ffmpeg', '-re', '-stream_loop', loops_number, '-i', video,
        '-c:v', 'copy', '-c:a', 'aac', '-ar', '44100', '-ac', '1',
        '-f', 'flv', 'rtmp://localhost:1935/live/video.flv'
    ]
    subprocess.run(ffmpeg_command)

    # Stop tcpdump capture, if required
    if capture_traffic:
        subprocess.run(['./tcpdump_utils/stop_capture.sh'])
        time.sleep(3)

if __name__ == "__main__":
    main()
