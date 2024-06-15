#!/bin/bash

# Function to print usage on terminal
function usage {
    echo "Usage: ./stream_video.sh [-i video] [-o] [-d]"
    echo "    -i video = input video filepath, with default value 'videos/big_buck_bunny_720p_5mb.mp4'"
    echo "    -o = stream the video once, without looping on it (the default behaviour is an infinite loop)"
    echo "    -d = disable the capture of the video stream outgoing packets through tcpdump (the capture is
                   enabled by default, with output file 'shared/server_out.pcap')"
    echo "    -c = start client to receive stream"
    echo "    -f client_output = name of the (.flv) client output file without extension (the default value
                                           is 'stream_output')"
    echo "    -x = disable the capture of the video stream incoming packets through tcpdump for client"
}

# Parse the script arguments
video="videos/big_buck_bunny_720p_5mb.mp4"
loops_number=-1
capture_traffic="true"
start_client="false"
client_out_file="stream_output.flv"
client_capture_traffic="true"
while getopts 'i:odcf:xh' OPTION; do
    case "$OPTION" in
        i)
            video="${OPTARG}"
            ;;
        o)
            loops_number=0
            ;;
        d)
            capture_traffic="false"
            ;;
        c)
            start_client="true"
            ;;
        f)
            client_out_file="${OPTARG}.flv"
            ;;
        x)
            client_capture_traffic="false"
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

# Function to start the client streaming
function start_client_streaming {
    if [ ${client_capture_traffic} == "true" ]; then
        ./tcpdump_utils/start_capture_client.sh
        sleep 2
    fi

    start_time=$(date +%s)
    ffmpeg -i rtmp://10.0.0.1:1935/live/video.flv -probesize 80000 -analyzeduration 15 -c:a copy -c:v copy "${client_out_file}"
    run_time=$(($(date +%s) - start_time))

    if [ ${client_capture_traffic} == "true" ]; then
        ./tcpdump_utils/stop_capture.sh
        sleep 3
    fi

    printf "\n"
    echo The stream acquisition run time is ${run_time}s
}

# Start tcpdump capture for server, if required
if [ ${capture_traffic} == "true" ]; then
    ./tcpdump_utils/start_capture_server.sh
    sleep 2
fi

# Stream the specified video on the server
ffmpeg -re -stream_loop "${loops_number}" -i "${video}" -c:v copy -c:a aac -ar 44100 -ac 1 \
       -f flv rtmp://localhost:1935/live/video.flv &

# If client streaming is enabled, start the client streaming
if [ ${start_client} == "true" ]; then
    start_client_streaming
fi

# Stop tcpdump capture for server, if required
if [ ${capture_traffic} == "true" ]; then
    ./tcpdump_utils/stop_capture.sh
    sleep 3
fi
