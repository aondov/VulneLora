#!/usr/bin/env python3

import subprocess
import os
import json
import re


service_path = "/opt/vulnelora"
sim_path = service_path + "/resources/lora-ap-sim/src"
save_flag = 0


args = {'target_ip':"127.0.0.1",
'target_port':25001,
'register': False,
'ap_id':"111111",
'shuffle': False,
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


def check_save():
	if save_flag == 0:
		print("\n>> Current configuration not saved, would you like to save it? [y/n] ", end='')
		save_req = input()

		if save_req.strip().lower() == "y":
			print("\n>> Enter path (including file name) where the configuration should be saved: ", end='')
			path = input()
			save_conf(path)
		elif save_req.strip().lower() == "n":
			pass
		else:
			print("\n>> Valid answers are 'y' or 'n'. Any other answers are interpreted same as 'n'.")


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
			return 1
	except ValueError:
		print("\n[ERROR]: Invalid input. Please enter a valid number.")
		return 1
	except Exception as e:
		print("[ERROR]: An unexpected error occured: ", e)
		check_save()
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
		print("[ERROR]: Could not change the specified parameter. Try again, please.")


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
		return 0


def extract(text, value):
	return text[len(value)+1:].strip()


def node_conf_validator(conf_type, value):
	if conf_type == "rssi":
		return -120 <= int(value) < 0
	elif conf_type == "snr":
		return -20 <= int(value) <= 15
	elif conf_type == "freq":
		pattern = re.compile(r'^86[6-8]\.\d{1,1}$')
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


def save_conf(path):
	with open(path, 'w') as file_w:
		json.dump(args, file_w)
	with open(path, 'r') as file_r:
		file_content = json.load(file_r)
		if file_content == args:
			global save_flag
			save_flag = 1
			print(f"\n>> [SUCCESS]: Current configuration saved successfully in '{path}'!")
		else:
			print("\n>> [ERROR]: Configuration has not beed saved correctly due to unknown error. Please, try again.")


def transfer_conf(loaded_conf):
	global args
	args.update(loaded_conf)


def validate_ip(ip):
	pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

	if re.match(pattern, ip):
		return True
	return False


def argument_parser():
	while True:
		print(f"\033[96m\nvulnelora\033[0m[\033[91mSimulation\033[0m]> ", end='')
		arg_input = input()

		if "help" in arg_input:
			with open(f"{service_path}/modes/help_messages/sim_mode.txt", 'r') as file:
				file_content = file.read()
				print(file_content)
		elif "nodes" in arg_input:
			tmp_nodes_num = extract(arg_input,'nodes')
			if not nodes_validator(tmp_nodes_num):
				args['nodes'] = int(tmp_nodes_num)
				print(f"\n>> Set argument: nodes={tmp_nodes_num}")
			else:
				args['nodes'] = 1
				print("\n>> Set argument: nodes=1 (revert to default value, the amount of nodes must be from 1 to 500)")
		elif "target_ip" in arg_input:
			tmp_server_ip = extract(arg_input,'target_ip')
			if validate_ip(tmp_server_ip):
				args['target_ip'] = tmp_server_ip
				print(f"\n>> Set argument: target_ip={tmp_server_ip}")
			else:
				args['target_ip'] = "127.0.0.1"
				print(f"\n>> Set argument: target_ip=127.0.0.1 (revert to default value, must be a valid IP address)")
		elif "target_port" in arg_input:
			tmp_port = extract(arg_input,'target_port')
			if validate_port(tmp_port):
				args['target_port'] = int(tmp_port)
				print(f"\n>> Set argument: target_port={tmp_port}")
			else:
				args['target_port'] = 8002
				print("\n>> Set argument: target_port=8002 (revert to default value, port must be from 1 to 65535)")
		elif "register" in arg_input:
			if arg_input == "register true":
				args['register'] = True
				print("\n>> Enabled argument: register")
			else:
				args['register'] = False
				print("\n>> Disabled argument: register")
		elif "shuffle" in arg_input:
			if arg_input == "shuffle true":
				args['shuffle'] = True
				print("\n>> Enabled argument: shuffle")
			else:
				args['shuffle'] = False
				print("\n>> Disabled argument: shuffle")
		elif "ap_id" in arg_input:
			tmp_dev_id = extract(arg_input,'ap_id')
			if validate_dev_id(tmp_dev_id):
				args['ap_id'] = tmp_dev_id
				print(f"\n>> Set argument: ap_id={tmp_dev_id}")
			else:
				args['ap_id'] = '111111'
				print("\n>> Set argument: ap_id=111111 (revert to default value, validation failed)")
		elif "node_path" in arg_input:
			tmp_node_path = extract(arg_input,'node_path')
			if validate_node_path(tmp_node_path):
				args['node_path'] = tmp_node_path
				print("\n>> Set argument: node_path={tmp_node_path}.")
			else:
				args['node_path'] = ""
				print("\n>> Set argument: node_path='' (revert to default value, validation failed)")
		elif "node_conf" in arg_input:
			if "node_conf rssi" in arg_input:
				tmp_rssi = extract(arg_input,'node_conf rssi')
				if node_conf_validator("rssi", tmp_rssi):
					args['node_conf']['rssi'] = tmp_rssi
					print(f"\n>> Set node config: rssi={tmp_rssi}")
				else:
					args['node_conf']['rssi'] = ""
					print("\n>> Set node config: rssi='' (revert to default value, rssi value must be from -120 to -1)")
			elif "node_conf snr" in arg_input:
				tmp_snr = extract(arg_input,'node_conf snr')
				if node_conf_validator("snr", tmp_snr):
					args['node_conf']['snr'] = tmp_snr
					print(f"\n>> Set node config: snr={tmp_snr}")
				else:
					args['node_conf']['snr'] = ""
					print("\n>> Set node config: snr='' (revert to default value, snr value must be from -20 to 10)")
			elif "node_conf freq" in arg_input:
				tmp_freq = extract(arg_input,'node_conf freq')
				if node_conf_validator("freq", tmp_freq):
					int_freq = int(float(tmp_freq) * 1000000)
					args['node_conf']['freq'] = str(int_freq)
					print(f"\n>> Set node config: frequency={int_freq}")
				else:
					print("\n>> Set node config: frequency='' (revert to default value, freq value must have format 868.N or 866.N)")
			elif "node_conf distance" in arg_input:
				tmp_dist = extract(arg_input,'node_conf distance')
				if node_conf_validator("distance", tmp_dist):
					args['node_conf']['distance'] = tmp_dist
					print(f"\n>> Set node config: distance={tmp_dist}")
				else:
					args['node_conf']['distance'] = ""
					print("\n>> Set node config: distance='' (revert to default value, distance value must be from 1 to 100)")
			elif "node_conf sf" in arg_input:
				tmp_sf = extract(arg_input,'node_conf sf')
				if node_conf_validator("sf", tmp_sf):
					args['node_conf']['sf'] = tmp_sf
					print(f"\n>> Set node config: sf={tmp_sf}")
				else:
					args['node_conf']['sf'] = ""
					print("\n>> Set node config: sf='' (revert to default value, sf value must be from 7 to 12)")
			elif "node_conf payload" in arg_input:
				tmp_payload = extract(arg_input,'node_conf payload')
				if node_conf_validator("payload", tmp_payload):
					args['node_conf']['payload'] = tmp_payload
					print(f"\n>> Set node config: payload={tmp_payload}")
				else:
					args['node_conf']['payload'] = ""
					print("\n>> Set node config: payload='' (revert to default value, payload must be less than 256 characters)")
			else:
				print("\n[ERROR]: Unknown end node configuration parameter. Type 'help' to see the supported parameters.")
		elif "save" in arg_input:
			tmp_path = extract(arg_input, 'save')
			if os.path.exists(tmp_path):
				print("\n>> Path to save current configuration already exists. Overwrite? [y/n] ", end='')
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
		elif "load" in arg_input:
			tmp_path = extract(arg_input, 'load')
			if os.path.exists(tmp_path):
				with open(tmp_path, 'r') as file:
					file_content = json.load(file)
					transfer_conf(file_content)
					if args == file_content:
						print("\n>> [SUCCESS]: Simulation configuration has been loaded successfully! Current argument configuration is:")
						print_args()
					else:
						print("\n>> [ERROR]: Simulation configuration has not been loaded due to unknown error. Please, try again.")
			else:
				print("\n>> [ERROR]: File does not exist.")
		elif arg_input == "print":
			print("\n>> Current argument configuration:")
			print_args()
		elif arg_input == "finish":
			print("\n>> Final argument configuration:")
			print_args()
			print()
			check_save()
			break
		elif arg_input == "exit":
			check_save()
			stop_sim(False, 0)
		else:
			print(f"\n[ERROR]: Unknown argument '{arg_input}'. Type 'help' to see the supported arguments.")


def generate_sim_command():
	replace_line(f"{sim_path}/generator.py", '# nodes_config_point', f"num_of_nodes = {str(args['nodes'])}")
	replace_line(f"{sim_path}/main.py", '# server_conf_point', f"    conn.connect(\"{args['target_ip']}\", {args['target_port']})")

	if args['node_conf']['rssi'] != "":
		replace_line(f"{sim_path}/node.py", '# rssi_conf_point', f"        rssi = {args['node_conf']['rssi']}")
	if args['node_conf']['snr'] != "":
		replace_line(f"{sim_path}/node.py", '# snr_conf_point', f"        snr = {args['node_conf']['snr']}")
	if args['node_conf']['freq'] != "":
		replace_line(f"{sim_path}/node.py", '# freq_conf_point', f"        freq = {args['node_conf']['freq']}")
	if args['node_conf']['distance'] != "":
		replace_line(f"{sim_path}/node.py", '# dist_conf_point', f"        distance = {args['node_conf']['distance']}")
	if args['node_conf']['sf'] != "":
		replace_line(f"{sim_path}/node.py", '# sf_conf_point', f"        sf = {args['node_conf']['sf']}")
	if args['node_conf']['payload'] != "":
		replace_line(f"{sim_path}/node.py", '# payload_conf_point', f"        app_data = \"{args['node_conf']['payload']}\"")

	subprocess.run(['python3', f"{sim_path}/generator.py"])

	if check_node_generator():
		print("\n[SUCCESS]: End nodes generated successfully!\n")
	else:
		print("[ERROR]: There was a problem generating the specified amount of end nodes.\n")
		check_save()
		stop_sim(False, 1)

	final_command = f"vulnelora -S -run \"-i {args['ap_id']}"

	if args['register'] == True:
		final_command = final_command + " -r"
	if args['shuffle'] == True:
		final_command = final_command + " -s"
	if args['node_path'] != "":
		final_command = final_command + f" -f {args['node_path']}"

	print(f"[SUCCESS]: Simulation configured, please run following command: {final_command}\"\n")


with open(f"{service_path}/modes/intro_messages/sim_mode.txt", 'r') as file:
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
