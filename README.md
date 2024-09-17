# Video_streaming

In this repository, I use COMNETSEMU to simulate a video stream application between a client and a server. The process involves streaming the video and capturing the packets of the video being streamed. 

To run the script, I first set up the client host and the server host. Within these hosts, I apply Docker to containerize the streaming application at both the client and the server. 
The `Topology.py` script is used to set up the network topology. This script configures the hosts, which are connected by two switches. Additionally, the script initiates the building of the Docker images and facilitates the video streaming process. The video streaming is performed for 10 seconds.

## Folders structure.
- **Server folder:**
  - Contains the video server Python script.
  - Contains the Dockerfile for the server.
  - Contains a video folder to store the streamed videos.
  - Contains an installation script for the necessary packages.

- **Client folder:**
  - Contains the client streaming Python script.
  - Contains a Dockerfile for the client.
  - Contains an installation file for the necessary packages.

- **pcap folder:**
  - Stores the generated pcap files.
- **Images:**
  - Stores necessary images.


![Alt Text](https://github.com/johnsengendo/Video_server/blob/main/images/Screenshot%202024-07-02%20100131.png)

## Steps to run the topology

1. **Run the `clean.sh` file** Which helps clear the Mininet network and also remove any existing containers.
   ```bash
   ./clean.sh

2. **Run the `build_docker_images.sh` file** To build the Docker images.
   ```bash
   ./build_docker_images.sh

3. **Run the `Topology.py` file** To build the tepology 
   ```bash
   sudo python3 Topology.py

**Below is a sample of the pcap file captured at the client side during streamimg which lasted for 10 seconds**

![Alt Text](https://github.com/johnsengendo/Video_server/blob/main/images/Screenshot%202024-07-01%20131138.png)
