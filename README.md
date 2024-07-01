# Video_streaming

In this repository, I use COMNETSEMU to simulate a video stream between a client and a server. The process involves streaming the video and capturing the packets of the video being streamed. 

To run the script, I first set up the client host and the server host. Within these hosts, I build Docker images that perform the streaming tasks at both the client and the server. The Topology.py script is used to set up the network topology. This script configures the hosts, which are connected by two switches. Additionally, the script initiates the building of the Docker images and facilitates the video streaming process.


![Alt Text](https://github.com/johnsengendo/Project/blob/main/Topology/Topology.png)

## Steps to Run the Simulation

1. **Run the `clean.sh` file**
   ```bash
   ./clean.sh

2. **Run the `build_docker_images.sh` file**
   ```bash
   ./build_docker_images.sh

3. **Run the `Topology.py` file**
   ```bash
   sudo python3 Topology.py
