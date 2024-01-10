#!/usr/bin/env python3

import subprocess
import os

service_path = "/opt/vulnelora"
sim_path = "/resources/lora-ap-sim/src"
num_of_nodes = 0
num_of_aps = 0

# sim_arguments
args = {'register':0, 'bandit':0, 'dev_id':'123456', 'shuffle':0, 'node_path':""}


def value_validator(value,type):
	upper_value = 1

	if type == "node":
		upper_value = 500
	elif type == "ap":
		upper_value = 5

	try:
		int_value = int(value)
		if 1 <= int_value <= upper_value:
			# print(f"Input fits within the range (1-{upper_value}).")
			return 0
		else:
			print(f"\n[ERROR]: Number of end nodes can only be within the range 1-{upper_value}. Please, try again.")
			return 1
	except ValueError:
		print("\n[ERROR]: Invalid input. Please enter a valid number.")
		return 1
	except Exception as e:
		print("[ERROR]: An unexpected error occured: ", e)
		exit(1)



def replace_line(file_path, search_string, replace_string):
	with open(file_path, 'r') as file:
		lines = file.readlines()

	found = False
	for i, line in enumerate(lines):
		if search_string in line:
			lines[i+1] = replace_string + '\n'  # Replacing the line with the new string
			found = True
			break

	if found:
		with open(file_path, 'w') as file:
			file.writelines(lines)
	else:
		print("[ERROR]: There was a problem generating the specified amount of end nodes.")


def check_node_generator():
	with open(service_path + sim_path + "/data/group.txt", 'r') as file:
		line_count = sum(1 for line in file)

	if line_count == int(num_of_nodes):
		return 0
	else:
		return 1

def validate_dev_id(value):
	dev_id_val = value[len('dev_id')+1:].strip().lower()
	return len(dev_id_val) == 6 and all(c.isalnum() and c.lower() in 'abcdef0123456789' for c in dev_id_val)


def validate_node_path(value):
	path_val = value[len('node_path')+1:].strip().lower()
	if os.path.exists(path_val):
		return os.path.getsize(path_val) > 0
	else:
		return 0


def extract(text, value):
	return text[len(value)+1:].strip().lower()


def argument_parser():
	while True:
		print(f"\033[96m\nvulora_arg_parse>\033[0m ", end='')
		arg_input = input()

		if "help" in arg_input:
			print("""\n\tregister [true|false]\tEnable/disable end node register process
\n\tshuffle [true|false]\tEnable/disable end node ID shuffle before start
\n\tbandit [true|false]\tEnable/disable support for bandit nodes
\n\tdev_id <dev_id_value>\tSet custom hardware ID for AP (default is 123456) - Allowed only hexadecimal characters
\n\tnode_path <path>\tSet path to custom LoRa node ID file (default is '') - Allowed only existing and non-empty files
\n\tprint\t\t\tPrint current argument configuration
\n\tfinish\t\t\tFinalize the argument configuration
\n\thelp\t\t\tPrint this help message""")
		elif "register" in arg_input:
			if "register true" in arg_input:
				args['register'] = 1
				print("\n>> Enabled argument: register")
			else:
				args['register'] = 0
				print("\n>> Disabled argument: register")
		elif "shuffle" in arg_input:
			if "shuffle true" in arg_input:
				args['shuffle'] = 1
				print("\n>> Enabled argument: shuffle")
			else:
				args['shuffle'] = 0
				print("\n>> Disabled argument: shuffle")
		elif "bandit" in arg_input:
			if "bandit true" in arg_input:
				args['bandit'] = 1
				print("\n>> Enabled argument: bandit")
			else:
				args['bandit'] = 0
				print("\n>> Disabled argument: bandit")
		elif "dev_id" in arg_input:
			if validate_dev_id(arg_input):
				tmp_dev_id = extract(arg_input,'dev_id')
				args['dev_id'] = tmp_dev_id
				print(f"\n>> Set argument: dev_id={tmp_dev_id}")
			else:
				args['dev_id'] = '123456'
				print("\n>> Set argument: dev_id=123456 (default value, validation failed)")
		elif "node_path" in arg_input:
			if validate_node_path(arg_input):
				tmp_node_path = extract(arg_input,'node_path')
				args['node_path'] = tmp_node_path
				print("\n>> Set argument: node_path={tmp_node_path}.")
			else:
				args['node_path'] = ""
				print("\n>> Set argument: node_path='' (default value, validation failed)")
		elif "print" in arg_input:
			print("\n>> Current argument configuration:")
			print(args)
		elif "finish" in arg_input:
			print("\n>> Final argument configuration:")
			print(args)
			print()
			break
		else:
			print(f"\n[ERROR]: Unknown argument '{arg_input}'. Type 'help' to see the supported arguments.")


with open(service_path + '/modes/intro_messages/sim_mode.txt', 'r') as file:
	file_content = file.read()
	print(file_content)

try:
	while True:
		num_of_nodes = input("\n> Enter a number of nodes to be generated (1-500): ")
		if not value_validator(num_of_nodes,"node"):
			break

	while True:
		num_of_aps = input("\n> Enter a number of APs to be generated (1-5): ")
		if not value_validator(num_of_aps,"ap"):
			break

	replace_line(service_path + sim_path + '/generator.py', '# nodes_config_point', 'num_of_nodes = ' + num_of_nodes)
	subprocess.run(['python3', service_path + sim_path + '/generator.py'])

	if not check_node_generator():
		print("\n[SUCCESS]: End nodes generated successfully!\n")
	else:
		print("[ERROR]: There was a problem generating the specified amount of end nodes.\n")

	argument_parser()

except KeyboardInterrupt:
	print("\n\n[INFO]: VulneLora forced to quit by keyboard interrupt. Bye Bye!\n")
	exit(0)

exit(0)
