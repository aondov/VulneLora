#!/usr/bin/env python3

import re
import os
import sys
import json
import subprocess


save_flag = 0
service_path = "/opt/vulnelora"
sim_path = f"{service_path}/resources/lora-ap-sim/src"


attack_config = {'target_ip': "127.0.0.1",
'target_port': 8002,
'ap_id': "9999",
'limit': 200000,
'delay': 500
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
            print(f"\n>> [SUCCESS]: Current attack configuration saved successfully in '{path}'!\n")
        else:
            print("\n>> [ERROR]: Attack configuration has not beed saved correctly due to unknown error. Please, try again.\n")


def transfer_conf(loaded_conf):
        global attack_config
        attack_config.update(loaded_conf)


def validate_ip(ip):
    pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

    if re.match(pattern, ip):
        return True
    return False


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


def reset_dos():
    replace_line(f"{sim_path}/run_dos.py", '# server_conf_point', '    conn.connect(\"127.0.0.1\", 8002)')
    replace_line(f"{sim_path}/run_dos.py", '# ap_id_conf_point', '    ap_id = str(random.randint(1000, 9999))')


def configure_dos():
    replace_line(f'{sim_path}/run_dos.py', '# server_conf_point', f"    conn.connect(\"{attack_config['target_ip']}\", {attack_config['target_port']})")
    replace_line(f'{sim_path}/run_dos.py', '# ap_id_conf_point', f"    ap_id = \"{attack_config['ap_id']}\"")


def argument_parser():
    argument = sys.argv[1]
    base_name, extension = os.path.splitext(argument)

    while True:
        print(f"\033[96m\nvulnelora\033[0m[\033[91m{base_name}\033[96m]>\033[0m ", end='')
        arg_input = input()

        if arg_input == "help":
            with open(service_path + '/modes/help_messages/dos_setr_flood.txt', 'r') as file:
                file_content = file.read()
                print(file_content)
        elif "target_ip" in arg_input:
            tmp_t_ip = extract(arg_input, "target_ip")
            if validate_ip(tmp_t_ip):
                attack_config['target_ip'] = tmp_t_ip
                print(f"\n>> Set argument: target_ip={tmp_t_ip}")
            else:
                attack_config['target_ip'] = "127.0.0.1"
                print("\n>> Set argument: target_ip=127.0.0.1 (revert to default value, must be a valid IP address)")
        elif "target_port" in arg_input:
            tmp_port = extract(arg_input, "target_port")
            try:
                if 1 <= int(tmp_port) <= 65535:
                    attack_config['target_port'] = int(tmp_port)
                    print(f"\n>> Set argument: target_port={tmp_port}")
                else:
                    raise ValueError()
            except ValueError:
                    attack_config['target_port'] = 8002
                    print("\n>> Set argument: target_port=8002 (revert to default value, target port must have a value from 1 to 65535)")
        elif "ap_id" in arg_input:
            tmp_id = extract(arg_input, "ap_id")
            if 1 <= len(tmp_id) <= 6:
                attack_config['ap_id'] = tmp_id
                print(f"\n>> Set argument: ap_id={tmp_id}")
            else:
                attack_config['ap_id'] = "9999"
                print("\n>> Set argument: ap_id='9999' (revert to default value, AP ID must have a length between 1 and 6 numbers)")
        elif "limit" in arg_input:
            tmp_limit = extract(arg_input, "limit")
            try:
                if 1 <= int(tmp_limit) <= 500000:
                    attack_config['limit'] = int(tmp_limit)
                    print(f"\n>> Set argument: limit={tmp_limit}")
                else:
                    raise ValueError()
            except ValueError:
                attack_config['limit'] = 200000
                print("\n>> Set argument: limit=200000 (revert to default value, limit must have a value from 1 to 500000)")
        elif "delay" in arg_input:
            tmp_delay = extract(arg_input, "delay")
            try:
                if 0 <= int(tmp_delay) <= 10000:
                    attack_config['delay'] = int(tmp_delay)
                    print(f"\n>> Set argument: delay={tmp_delay}")
                else:
                    raise ValueError()
            except ValueError:
                attack_config['delay'] = 0
                print("\n>> Set argument: delay=0 (revert to default value, delay must have a value from 0 to 10)")
        elif arg_input == "print":
            print("\n>> Current argument configuration:")
            print_args()
        elif "save" in arg_input and "load" not in arg_input:
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
                        print("\n>> [SUCCESS]: Attack configuration has been loaded successfully! Current configuration is:\n")
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
            exit(0)
        else:
            print(f"\n[ERROR]: Unknown argument '{arg_input}'. Type 'help' to see the supported arguments.")



def run_attack():
    configure_dos()
    subprocess.run(["python3", f"{service_path}/resources/lora-ap-sim/src/run_dos.py", f"{attack_config['delay']}", f"{attack_config['limit']}"])


if __name__ == "__main__":
    try:
        reset_dos()
        argument_parser()
        run_attack()
    except KeyboardInterrupt:
        exit(0)

    exit(0)
