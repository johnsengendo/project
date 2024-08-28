import subprocess
import os
import threading
from comnetsemu.cli import CLI
from comnetsemu.net import Containernet, VNFManager
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.node import Controller

# Start the server
def start_server():
    subprocess.run(['docker', 'exec', '-it', 'streaming_server', 'bash', '-c', 'cd /home && python3 video_streaming.py'])

# Start the client
def start_client():
    subprocess.run(['docker', 'exec', '-it', 'streaming_client', 'bash', '-c', 'cd /home && python3 get_video_streamed.py'])

# Main function
if __name__ == '__main__':
    setLogLevel('info')
    
    # Prepare shared folder to store the pcap files
    script_directory = os.path.abspath(os.path.dirname(__file__))
    shared_directory = os.path.join(script_directory, 'pcap')

    if not os.path.exists(shared_directory):
        os.makedirs(shared_directory)

    # Create network and VNF manager
    net = Containernet(controller=Controller, link=TCLink, xterms=False)
    mgr = VNFManager(net)

    info('*** Add controller\n')
    net.addController('c0')

    info('*** Creating hosts\n')
    server = net.addDockerHost('server', dimage='dev_test', ip='10.0.0.1', docker_args={'hostname': 'server'})
    client = net.addDockerHost('client', dimage='dev_test', ip='10.0.0.2', docker_args={'hostname': 'client'})

    info('*** Adding switches and links\n')
    switch1 = net.addSwitch('s1')
    switch2 = net.addSwitch('s2')
    
    net.addLink(switch1, server)
    net.addLink(switch2, client)
    middle_link = net.addLink(switch1, switch2, bw=10, delay='5ms')

    info('\n*** Starting network\n')
    net.start()

    info("*** Client host pings the server to test for connectivity: \n")
    reply = client.cmd("ping -c 5 10.0.0.1")
    print(reply)

    # Add containers
    streaming_server = mgr.addContainer('streaming_server', 'server', 'streaming_server_image', '', docker_args={'volumes': {shared_directory: {'bind': '/home/pcap/', 'mode': 'rw'}}})
    streaming_client = mgr.addContainer('streaming_client', 'client', 'streaming_client_image', '', docker_args={'volumes': {shared_directory: {'bind': '/home/pcap/', 'mode': 'rw'}}})

    # Start packet capture on both server and client before starting the streaming process
    capture_file = '/home/pcap/capture.pcap'
    server.cmd(f'tshark -i eth0 -w {capture_file} &')
    client.cmd(f'tshark -i eth0 -w {capture_file} &')

    # Start the server and client threads
    server_thread = threading.Thread(target=start_server)
    client_thread = threading.Thread(target=start_client)
    server_thread.start()
    client_thread.start()
    server_thread.join()
    client_thread.join()

    # Adjust bandwidth and delay, then rerun the streaming process
    for bandwidth, delay in [(8, '6ms'), (5, '10ms')]:
        info(f"\n*** Adjusting middle link to bandwidth {bandwidth} Mbps and delay {delay}\n")
        middle_link.intf1.config(bw=bandwidth, delay=delay)

        # Re-run the streaming process with new parameters
        server_thread = threading.Thread(target=start_server)
        client_thread = threading.Thread(target=start_client)
        server_thread.start()
        client_thread.start()
        server_thread.join()
        client_thread.join()

    if not args.autotest:
        CLI(net)

    mgr.removeContainer('streaming_server')
    mgr.removeContainer('streaming_client')
    net.stop()
    mgr.stop()
