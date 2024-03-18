#!/usr/bin/env python3


# ===== WELCOME TO VULNELORA TEMPLATE SCRIPT! =====
#
# In here, you can create your own attack and implement it to VulneLora. Just follow the steps below,
# but don't hesitate to tweak the script according to your needs.
#
# Every attack is saved to the 'attacks/<technology>/<script_name>' directory, in case you need to
# find other attacks for inspiration.
#
# You are free to delete the template comments in this file, although we recommend keeping them
# if you need some help.
#
# Happy IoT testing!
# 	- Team VulneLora


import subprocess
import sys
import os
import re
import json
import threading

# TIP: Don't forget to import necessary packages

service_path = "/opt/vulnelora" # Path to the whole VulneLora package directory
save_flag = 0

# STEP 1: Create a dictionary with necessary variables that represent attack configuration.
#
# Example:
#
# attack_config_example = {
# 'target_ip': "127.0.0.1",
# 'target_port': 1234,
# 'payload': "template"
# }
#
# ===== CONFIG DICT =====

attack_config = {}

# ===== CONFIG DICT =====


# Validation function to check if the save directory already exists and if it is a valid path
def check_save():
    if save_flag == 0:
        print("\n>> Current attack configuration not saved, would you like to save it? [y/n] ", end='')
        save_req = input()

        if save_req.strip().lower() == "y":
            print("\n>> Enter path (including file name) where the attack configuration should be saved: ", end='')
            path = input()
            save_conf(path)
        elif save_req.strip().lower() == "n":
            pass
        else:
            print("\n>> Valid answers are 'y' or 'n'. Any other answers are interpreted same as 'n'.")


# Function to separate value from argument (used in argument_parser)
def extract(text, value):
    return text[len(value)+1:].strip()


# Function to check if the input path exists and if it is an empty file
def validate_path(value):
    if os.path.exists(value):
        return os.path.getsize(value) > 0
    else:
        return 0


# Function to print current attack configuration
def print_args():
    formatted_args = json.dumps(attack_config, indent=4)
    print(formatted_args)


# Function to save a current attack configuration
def save_conf(path):
    with open(path, 'w') as file_w:
        json.dump(attack_config, file_w)
    with open(path, 'r') as file_r:
        file_content = json.load(file_r)
        if file_content == attack_config:
            global save_flag
            save_flag = 1
            print(f"\n>> [SUCCESS]: Current attack configuration saved successfully in '{path}'!")
        else:
            print("\n>> [ERROR]: Attack configuration has not beed saved correctly due to unknown error. Please, try again.")


# Function to load new attack configuration to the attack dictionary
def transfer_conf(loaded_conf):
        global attack_config
        attack_config.update(loaded_conf)


# Function to validate the IP address correct format
def validate_ip(ip):
    pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

    if re.match(pattern, ip):
        return True
    return False


# STEP 3: Add own functions and validators
#
# ===== CUSTOM FUNCTIONS =====

def hello_world():
    print("Hello world!")

# ===== CUSTOM FUNCTIONS =====


def argument_parser():
    argument = sys.argv[1]
    base_name, extension = os.path.splitext(argument)

    while True:
        print(f"\033[96m\nvulnelora\033[0m[\033[91m{base_name}\033[96m]>\033[0m ", end='')
        arg_input = input()

# STEP 2: Add your own arguments in this parser function to configure attack.
#
# For the example dictionary attack_config_example, we added a few lines of
# code which parse keys in the example dictionary.
#
# First parsed parameter also includes a commentary on every step, which
# should be included in every parameter parse process.
#
#	===== EXAMPLE PARSER =====
#
#        if "target_ip" in arg_input:
#            tmp_target_ip = extract(arg_input, "target_ip") # Extract the value after argument name
#            if validate_ip(tmp_target_ip): # Validate format
#                attack_config_example['target_ip'] = tmp_target_ip # Save value to the attack config dict (if valid)
#                print(f"\n>> Set argument: target_ip={tmp_target_ip}") # Print a confirmation message
#            else:
#                attack_config_example['target_ip'] = "127.0.0.1" # Revert to default value (if not valid)
#                print(f"\n>> Set argument: target_ip=127.0.0.1 (revert to default value, must be a valid IP address)") # Print an information message
#
#        elif "target_port" in arg_input:
#            tmp_target_port = extract(arg_input, "target_port")
#            try:
#                int_tmp_port = int(tmp_target_port)
#                if 1 <= int_tmp_port <= 65535:
#                    attack_config_example['target_port'] = int_tmp_port
#                    print(f"\n>> Set argument: target_port={int_tmp_port}")
#                else:
#                    raise ValueError()
#            except ValueError:
#                attack_config_example['target_port'] = 22
#                print(f"\n>> Set argument: target_port=22 (revert to default value, port must be from 1 to 65535)")
#
#        elif "payload" in arg_input:
#            tmp_payload = extract(arg_input, "payload")
#            attack_config_example['payload'] = tmp_payload
#            print(f"\n>> Set argument: payload={tmp_payload}")
#
#	===== EXAMPLE PARSER =====
#
# Every function used in this example is described directly in its body.
# User is allowed to use own functions, which were added by the user.

# TIP: Don't forget to create a help message for the attack.
# Choose whatever format you prefer.
#
# ===== HELP MESSAGE =====

        if arg_input == "help": # Print help message
            with open(f"{service_path}/modes/help_messages/placeholder.txt", 'r') as file: # Set a correct path to the help message
                file_content = file.read()
                print(file_content)

# ===== HELP MESSAGE =====
#
# TIP: We recommend leaving the parsers below untouched. ;)

        elif arg_input == "print": # Print current attack configuration
            print("\n>> Current argument configuration:")
            print_args()
        elif "save" in arg_input: # Save configuration to file
            tmp_path = extract(arg_input, 'save')
            if validate_path(tmp_path):
                print("\n>> Path to save current attack configuration already exists. Overwrite? [y/n] ", end='')
                overwrite = input()
                if overwrite.strip().lower() == "y":
                    save_conf(tmp_path)
                elif overwrite.strip().lower() == "n":
                    pass
                else:
                    print("\n>> Valid answers are 'y' or 'n'. Any other answers are interpreted same as 'n'.")
            else:
                if tmp_path != "":
                    save_conf(tmp_path)
                else:
                    print("\n>> [ERROR]: Attack configuration not saved. Please, input a valid path (including file name).")
        elif "load" in arg_input: # Load configuration from file
            tmp_path = extract(arg_input, 'load')
            if validate_path(tmp_path) and tmp_path != "":
                with open(tmp_path, 'r') as file:
                    file_content = json.load(file)
                    transfer_conf(file_content)
                    if attack_config == file_content:
                        print("\n>> [SUCCESS]: Attack configuration has been loaded successfully! Current configuration is:")
                        print_args()
                    else:
                        print("\n>> [ERROR]: Attack configuration has not been loaded due to unknown error. Please, try again.")
            else:
                print("\n>> [ERROR]: File does not exist.")
        elif arg_input == "finish": # Finish the attack configuration and start the attack
            print("\n>> Final attack configuration:")
            print_args()
            print()
            check_save()
            break
        elif arg_input == "exit": # Exit VulneLora
            check_save()
            exit(0)
        else:
            print(f"\n[ERROR]: Unknown argument '{arg_input}'. Type 'help' to see the supported arguments.")


if __name__ == "__main__":
    try:
        argument_parser() # First, start the argument parser (attack configuration)

# STEP 4: Add your main program here
#
# ===== PROGRAM MAIN =====

        hello_world()

# ===== PROGRAM MAIN =====

    except KeyboardInterrupt:
        exit(0)

    exit(0)
