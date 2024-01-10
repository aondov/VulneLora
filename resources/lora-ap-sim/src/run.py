#!/usr/bin/python

import sys
import subprocess
import os
import signal

first_id = 111100
last_id = 111120
first_group = 10
last_group = 20
processes = []
register = 1

print("Loading APs configuration...")


def main(argv):
    """
    Multi-AP processing
    :param argv: command line arguments
    :return
    """
    # dirname = os.getcwd()
    group_id = first_group
    for ap_id in range(first_id, last_id):
        file = "data/group{0}.txt".format(group_id)

        if register == 1:
            command = "python main.py -i {0} -r -s -f {1} &".format(ap_id, file)
        else:
            command = "python main.py -i {0} -s -f {1} &".format(ap_id, file)

        command_list = command.split()
        processes.append(subprocess.Popen(command_list))
        group_id += 1

        if group_id > last_group:
            group_id = first_group
        # time.sleep(1)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        # Killing processes on keyboard interrupt
        for process in processes:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        print("LoRa Access Point simulator closed!")
