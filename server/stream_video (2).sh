#!/bin/bash

# Function to print usage on terminal
function usage {
    echo "Usage: ./stream_and_get.sh [-i video] [-o stream_output_filename] [-s] [-d]"
    echo "    -i video = input video filepath, with default value 'videos/big_buck_bunny_720p_5mb.mp4'"
    echo "    -o stream_output_filename = name of the (.flv) output file without extension (the default value
                                          is 'stream_output')"
    echo "    -s = stream the video once, without looping on it (the default behaviour is an infinite loop)"
    echo "    -d = disable the capture of the video stream packets through tcpdump (the capture is
                   enabled by default, with output files 'shared/server_out.pcap' and 'shared/client_in.pcap')"
}

# Parse the script arguments
video="videos/big_buck_bunny_720p_5mb.mp4"
out_file="stream_output.flv"
loops_number=-1
capture_traffic="true"
while getopts 'i:o:shsd' OPTION; do
    case "$OPTION" in
        i)
            video="${OPTARG}"
            ;;
        o)
            out_file="${OPTARG}.flv"
            ;;
        s)
            loops_number=0
            ;;
        d)
            capture_traffic="false"
            ;;
        h)
            usage
            exit 0
            ;;
        *)
            usage
            exit 0
            ;;
    esac
done
shift "$((OPTIND -1))"

# Start tcpdump capture, if required
if [ ${capture_traffic} == "true" ]; then
    ./tcpdump_utils/start_capture_server.sh &
    server_tcpdump_pid=$!
    sleep 2
    ./tcpdump_utils/start_capture_client.sh &
    client_tcpdump_pid=$!
    sleep 2
fi

# Stream the specified video
ffmpeg -re -i "${video}" -c:v libx264 -preset ultrafast -tune zerolatency -b:v 1M -maxrate 1M -bufsize 1M \
       -c:a aac -b:a 128k -ar 44100 -f flv -timeout 10 rtmp://localhost:1935/live/video.flv

# Get the video stream and save it to the specified file
start_time=$(date +%s)
ffmpeg -i rtmp://10.0.0.1:1935/live/video.flv -probesize 80000 -analyzeduration 15 -c:a copy -c:v copy -timeout 10 "${out_file}"
run_time=$(($(date +%s) - start_time))

# Stop tcpdump capture, if required
if [ ${capture_traffic} == "true" ]; then
    ./tcpdump_utils/stop_capture1.sh
    sleep 3
fi

# Stop tcpdump capture, if required
if [ ${capture_traffic} == "true" ]; then
    ./tcpdump_utils/stop_capture2.sh
    sleep 3
fi

# Print the stream acquisition run time
printf "\n"
echo The stream acquisition run time is ${run_time}s