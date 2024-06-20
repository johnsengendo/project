#! /usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
import os
import signal

def stop_capture():
    # Get the PID of the tcpdump process
    ps_output = subprocess.check_output(['ps', '-e']).decode('utf-8')
    for line in ps_output.splitlines():
        if 'tcpdump' in line:
            pid = int(line.split()[0])
            # Send SIGINT (signal number 2 in bash)
            os.kill(pid, signal.SIGINT)
            break

if __name__ == "__main__":
    stop_capture()
