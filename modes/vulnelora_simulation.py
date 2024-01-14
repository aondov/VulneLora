#!/usr/bin/env python3

import subprocess
import os
import json
import re

service_path = "/opt/vulnelora"
sim_path = service_path + "/resources/lora-ap-sim/src"

# sim_arguments
args = {'server':"127.0.0.1",
'port':8002,
'register':0,
'dev_id':"111111",
'shuffle':0,
'nodes':1,
'node_path':"",
'node_conf':{
	'rssi':"",
	'snr':"",
	'freq':"",
	'payload':"",
	'sf':"",
	'distance':""
	}
}


def stop_sim(reset_only, ret_value):
	replace_line(sim_path + '/node.py', '# rssi_conf_point', '        rssi = LoRa.calculate_rssi(power, TRANS_ANT_GAIN, REC_ANT_GAIN, freq / 1000000, distance)')
	replace_line(sim_path + '/node.py', '# snr_conf_point', '        snr = LoRa.get_snr()')
	replace_line(sim_path + '/node.py', '# freq_conf_point', '        freq = freq')
	replace_line(sim_path + '/node.py', '# dist_conf_point', '        distance = self._get_distance_in_km(MAX_X_POSITION / 2, MAX_Y_POSITION / 2)')
	replace_line(sim_path + '/node.py', '# sf_conf_point', '        sf = sf')
	replace_line(sim_path + '/node.py', '# payload_conf_point', '        app_data = LoRa.get_data(self.x, self.y)')
	replace_line(sim_path + '/main.py', '# server_conf_point', '    conn.connect(\"127.0.0.1\", 8002)')

	if not reset_only:
		exit(ret_value)


def print_args():
	formatted_args = json.dumps(args, indent=4)
	print(formatted_args)


def nodes_validator(value):
	upper_value = 500

	try:
		int_value = int(value)
		if 1 <= int_value <= upper_value:
			return 0
		else:
			print(f"\n[ERROR]: Number of end nodes can only be within the range 1-{upper_value}. Please, try again.")
			return 1
	except ValueError:
		print("\n[ERROR]: Invalid input. Please enter a valid number.")
		return 1
	except Exception as e:
		print("[ERROR]: An unexpected error occured: ", e)
		stop_sim(False, 1)



def replace_line(file_path, search_string, replace_string):
	with open(file_path, 'r') as file:
		lines = file.readlines()

	found = False
	for i, line in enumerate(lines):
		if search_string in line:
			lines[i+1] = replace_string + '\n'
			found = True
			break

	if found:
		with open(file_path, 'w') as file:
			file.writelines(lines)
	else:
		print("[ERROR]: There was a problem generating the specified amount of end nodes.")


def check_node_generator():
	with open(sim_path + "/data/group.txt", 'r') as file:
		line_count = sum(1 for line in file)

	return line_count == int(args['nodes'])


def validate_dev_id(value):
	return len(value) == 6 and all(c.isalnum() and c.lower() in 'abcdef0123456789' for c in value)


def validate_node_path(value):
	if os.path.exists(value):
		return os.path.getsize(value) > 0
	else:
		return 0


def validate_port(value):
	try:
		int_port = int(value)
		return (1 <= int_port <= 65535)
	except ValueError:
		print("[ERROR]: Port value must be in range 1-65535.")
		return 0


def extract(text, value):
	return text[len(value)+1:].strip()


def node_conf_validator(conf_type, value):
	if conf_type == "rssi":
		return -130 <= int(value) < 0
	elif conf_type == "snr":
		return -20 <= int(value) <= 10
	elif conf_type == "freq":
		pattern = re.compile(r'^86[6-8]\.\d{1,3}$')
		if pattern.match(value):
			return 1
		else:
			return 0
	elif conf_type == "distance":
		return 0 <= int(value) <= 100
	elif conf_type == "payload":
		return 0 < len(str(value)) <= 255
	elif conf_type == "sf":
		if int(value) in {7, 8, 9, 10, 11, 12}:
			return 1
		else:
			return 0
	else:
		return 0


def argument_parser():
	while True:
		print(f"\033[96m\nvulora_sim>\033[0m ", end='')
		arg_input = input()

		if "help" in arg_input:
			with open(service_path + '/modes/help_messages/sim_mode.txt', 'r') as file:
				file_content = file.read()
				print(file_content)
		elif "nodes" in arg_input:
			tmp_nodes_num = extract(arg_input,'nodes')
			if not nodes_validator(tmp_nodes_num):
				args['nodes'] = int(tmp_nodes_num)
				print(f"\n>> Set argument: nodes={tmp_nodes_num}")
			else:
				args['nodes'] = 1
				print("\n>> Set argument: nodes=1 (default value, validation failed)")
		elif "server" in arg_input:
			tmp_server_ip = extract(arg_input,'server')
			args['server'] = tmp_server_ip
			print(f"\n>> Set argument: server={tmp_server_ip}")
		elif "port" in arg_input:
			tmp_port = extract(arg_input,'port')
			if validate_port(tmp_port):
				args['port'] = int(tmp_port)
				print(f"\n>> Set argument: port={tmp_port}")
			else:
				args['port'] = 8002
				print("\n>> Set argument: port=8002 (default value, validation failed)")
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
		elif "dev_id" in arg_input:
			tmp_dev_id = extract(arg_input,'dev_id')
			if validate_dev_id(tmp_dev_id):
				args['dev_id'] = tmp_dev_id
				print(f"\n>> Set argument: dev_id={tmp_dev_id}")
			else:
				args['dev_id'] = '111111'
				print("\n>> Set argument: dev_id=111111 (default value, validation failed)")
		elif "node_path" in arg_input:
			tmp_node_path = extract(arg_input,'node_path')
			if validate_node_path(tmp_node_path):
				args['node_path'] = tmp_node_path
				print("\n>> Set argument: node_path={tmp_node_path}.")
			else:
				args['node_path'] = ""
				print("\n>> Set argument: node_path='' (default value, validation failed)")
		elif "node_conf" in arg_input:
			if "node_conf rssi" in arg_input:
				tmp_rssi = extract(arg_input,'node_conf rssi')
				if node_conf_validator("rssi", tmp_rssi):
					args['node_conf']['rssi'] = tmp_rssi
					print(f"\n>> Set node config: rssi={tmp_rssi}")
				else:
					args['node_conf']['rssi'] = ""
					print("\n>> Set node config: rssi=\"\" (default value, validation failed)")
			elif "node_conf snr" in arg_input:
				tmp_snr = extract(arg_input,'node_conf snr')
				if node_conf_validator("snr", tmp_snr):
					args['node_conf']['snr'] = tmp_snr
					print(f"\n>> Set node config: snr={tmp_snr}")
				else:
					args['node_conf']['snr'] = ""
					print("\n>> Set node config: snr=\"\" (default value, validation failed)")
			elif "node_conf freq" in arg_input:
				tmp_freq = extract(arg_input,'node_conf freq')
				if node_conf_validator("freq", tmp_freq):
					int_freq = int(float(tmp_freq) * 1000000)
					args['node_conf']['freq'] = str(int_freq)
					print(f"\n>> Set node config: frequency={int_freq}")
				else:
					print("\n>> Set node config: frequency=\"\" (default value, validation failed)")
			elif "node_conf distance" in arg_input:
				tmp_dist = extract(arg_input,'node_conf distance')
				if node_conf_validator("distance", tmp_dist):
					args['node_conf']['distance'] = tmp_dist
					print(f"\n>> Set node config: distance={tmp_dist}")
				else:
					args['node_conf']['distance'] = ""
					print("\n>> Set node config: distance=\"\" (default value, validation failed)")
			elif "node_conf sf" in arg_input:
				tmp_sf = extract(arg_input,'node_conf sf')
				if node_conf_validator("sf", tmp_sf):
					args['node_conf']['sf'] = tmp_sf
					print(f"\n>> Set node config: sf={tmp_sf}")
				else:
					args['node_conf']['sf'] = ""
					print("\n>> Set node config: sf=\"\" (default value, validation failed)")
			elif "node_conf payload" in arg_input:
				tmp_payload = extract(arg_input,'node_conf payload')
				if node_conf_validator("payload", tmp_payload):
					args['node_conf']['payload'] = tmp_payload
					print(f"\n>> Set node config: payload={tmp_payload}")
				else:
					args['node_conf']['payload'] = ""
					print("\n>> Set node config: payload=\"\" (default value, validation failed)")
			else:
				print("\n[ERROR]: Unknown end node configuration parameter. Type 'help' to see the supported parameters.")
		elif arg_input == "print":
			print("\n>> Current argument configuration:")
			print_args()
		elif arg_input == "finish":
			print("\n>> Final argument configuration:")
			print_args()
			print()
			break
		elif arg_input == "exit":
			stop_sim(False, 0)
		else:
			print(f"\n[ERROR]: Unknown argument '{arg_input}'. Type 'help' to see the supported arguments.")


def generate_sim_command():
	replace_line(sim_path + '/generator.py', '# nodes_config_point', 'num_of_nodes = ' + str(args['nodes']))
	replace_line(sim_path + '/main.py', '# server_conf_point', '    conn.connect(\"' + args['server'] + '\", ' + str(args['port']) + ')')

	if args['node_conf']['rssi'] != "":
		replace_line(sim_path + '/node.py', '# rssi_conf_point', '        rssi = ' + args['node_conf']['rssi'])
	if args['node_conf']['snr'] != "":
		replace_line(sim_path + '/node.py', '# snr_conf_point', '        snr = ' + args['node_conf']['snr'])
	if args['node_conf']['freq'] != "":
		replace_line(sim_path + '/node.py', '# freq_conf_point', '        freq = ' + args['node_conf']['freq'])
	if args['node_conf']['distance'] != "":
		replace_line(sim_path + '/node.py', '# dist_conf_point', '        distance = ' + args['node_conf']['distance'])
	if args['node_conf']['sf'] != "":
		replace_line(sim_path + '/node.py', '# sf_conf_point', '        sf = ' + args['node_conf']['sf'])
	if args['node_conf']['payload'] != "":
		replace_line(sim_path + '/node.py', '# payload_conf_point', '        app_data = \"' + args['node_conf']['payload'] + '\"')

	subprocess.run(['python3', sim_path + '/generator.py'])

	if check_node_generator():
		print("\n[SUCCESS]: End nodes generated successfully!\n")
	else:
		print("[ERROR]: There was a problem generating the specified amount of end nodes.\n")
		stop_sim(False, 1)

	final_command = "vulnelora -S -run \"-i " + args['dev_id']

	if args['register'] == 1:
		final_command = final_command + " -r"
	if args['shuffle'] == 1:
		final_command = final_command + " -s"
	if args['node_path'] != "":
		final_command = final_command + " -f " + args['node_path']

	print("[SUCCESS]: Simulation configured, please run following command: " + final_command + "\"\n")


with open(service_path + '/modes/intro_messages/sim_mode.txt', 'r') as file:
	file_content = file.read()
	print(file_content)

try:
	stop_sim(True, 0)
	argument_parser()
	generate_sim_command()

except KeyboardInterrupt:
	print("\n\n[INFO]: VulneLora forced to quit by keyboard interrupt. Bye Bye!\n")
	stop_sim(False, 0)

exit(0)
