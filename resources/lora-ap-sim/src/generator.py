#!/usr/bin/python

import random
import string

dev_ids = []
file_path = "/opt/vulnelora/resources/lora-ap-sim/src/data/group.txt"
# nodes_config_point
num_of_nodes = 5


def generate_nodes(number_of_nodes=5, dev_id_length=4):
    """
    Generate nodes and save them to local array
    :param number_of_nodes: int, default is 500
    :param dev_id_length: int, default and recommended is 4
    :return
    """
    for x in range(number_of_nodes):
        dev_ids.append(''.join(random.choices(string.ascii_letters + string.digits, k=dev_id_length)))


def save_nodes(path=file_path):
    """
    Save list of nodes in dev_id array to a file
    :param path: string, relative or absolute path to new file, path must exists
    :return
    """
    file = open(path, "w")
    for dev_id in dev_ids:
        file.write(dev_id + "\n")
    file.close()


def load_nodes(path=file_path):
    """
    Load list of nodes and returns it
    :param path: path: string, relative or absolute path to new file, path must exists
    :return list, list containing lot of ids
    """
    ids = []
    file = open(path, "r")
    for line in file:
        ids.append(line.strip())
    file.close()
    return ids

generate_nodes(num_of_nodes, 4)
save_nodes(file_path)
