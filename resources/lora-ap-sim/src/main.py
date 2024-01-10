#!/usr/bin/python

import getopt
import sys
import random
import time

from multiprocessing import Process, Queue
from access_point import AccessPoint
from connection_controller import ConnectionController
from end_node import EndNode
from bandit_node import BanditNode
from generator import load_nodes
from helper import Helper
from queued_message import QueuedReply
from lora import MAX_X_POSITION, MAX_Y_POSITION

sock = None
conn = None


def read_reply(queue, access_point, nodes):
    """
    Read a reply received on main thread
    :param queue: Queue
    :param access_point: AccessPoint
    :param nodes: dict, containing al nodes
    :return void
    """
    message = queue.get(timeout=1)
    reply = conn.send_data(message.json_message)

    if reply is not None:
        reply_dict = Helper.from_json(reply)
        queued_reply = QueuedReply(message.id, reply_dict)

        dev_id = reply_dict['message_body']['dev_id']

        if access_point.duty_cycle_na != 1:
            toa = nodes[dev_id].process_reply(queued_reply, access_point.duty_cycle)
        else:
            nodes[dev_id].collisions += 1
            print("Could not send any downlink messages till next duty cycle refresh")
            toa = 0

        if toa is not None:
            access_point.set_remaining_duty_cycle(toa)


def main(argv):
    """
    Main program method
    :param argv: command line arguments
    :return
    """
    ap_id = '111111'
    register_nodes = False
    shuffle_nodes = False
    duty_cycle_na = 0
    node_file = "data/group1.txt"
    bandit_nodes = False
    algorithm = 'ucb'
    test_scenario = False
    max_x = MAX_X_POSITION
    max_y = MAX_Y_POSITION

    # Reading arguments from command line
    try:
        opts, args = getopt.getopt(argv, "hi:rsf:ab:t", ["id=", "file=", "help", "register", "shuffle", "bandit=", "test"])
    except getopt.GetoptError:
        print("main.py -i <access-point-id> [-f <file-path> -r -s -b <algorithm> -t]")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print("main.py -i <access-point-id>\n")
            print("-i <dev_id>, --id=<dev_id>\t- Specify LoRa AP hardware id")
            print("-r, --register\t\t- Include end nodes registration process")
            print("-s, --shuffle\t\t- Shuffle list of end nodes")
            print("-f <file_path>, --file=<file_path>\t- Specify LoRa node id file")
            print("-b <algorithm>, --bandit\t- Activates bandit nodes and select UCB or TS algorithm")
            print("-t, --test\t- Using test scenario for developing purposes")
            sys.exit(0)
        elif opt in ("-i", "--id"):
            ap_id = arg
        elif opt in ("-r", "--regen"):
            register_nodes = True
        elif opt in ("-s", "--shuffle"):
            shuffle_nodes = True
        elif opt in ("-f", "--file"):
            node_file = arg
        elif opt in ("-b", "--bandit"):
            bandit_nodes = True
            algorithm = arg
        elif opt in ("-t", "--test"):
            test_scenario = True

    # If there was an AP id defined
    conn.connect('lora.fiit.stuba.sk', 25001)
    access_point = AccessPoint(ap_id, conn)
    access_point.send_setr()

    if test_scenario:
        node_ids = ['KmoT', 'meQy', 'meBh', 'cbun', 'ttYa']
    else:
        node_ids = load_nodes(node_file)

    if shuffle_nodes:
        random.shuffle(node_ids)

    nodes = {}
    processes = {}

    message_queue = Queue()
    emergency_queue = Queue()
    num_of_nodes = 0

    while True:
        while not message_queue.empty() or not emergency_queue.empty():
            try:
                while not emergency_queue.empty():
                    read_reply(emergency_queue, access_point, nodes)

                read_reply(message_queue, access_point, nodes)
            except Exception as qe:
                print(qe)

            # Other nodes joins later
            if num_of_nodes < len(node_ids):
                node_id = node_ids[num_of_nodes]

                if bandit_nodes:
                    node = BanditNode(node_id, algorithm, register_nodes)
                else:
                    node = EndNode(node_id, register_nodes)

                process = Process(target=node.device_routine, args=(message_queue, emergency_queue,))
                process.daemon = True
                process.start()
                processes[node_id] = process
                nodes[node_id] = node
                num_of_nodes += 1

        if num_of_nodes < len(node_ids):
            node_id = node_ids[num_of_nodes]
            if bandit_nodes:
                node = BanditNode(node_id, algorithm, register_nodes)
            else:
                node = EndNode(node_id, register_nodes)

            process = Process(target=node.device_routine, args=(message_queue, emergency_queue,))
            process.daemon = True
            process.start()
            processes[node_id] = process
            nodes[node_id] = node
            num_of_nodes += 1
            # time.sleep(random.randrange(2))


if __name__ == "__main__":
    try:
        conn = ConnectionController()
        main(sys.argv[1:])
    except KeyboardInterrupt as e:
        if conn is not None:
            conn.close()
            print("Connection closed")

        print("Python script finished")
