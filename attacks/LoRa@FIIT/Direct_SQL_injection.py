import os
import sys
import json
import subprocess


save_flag = 0
service_path = "/opt/vulnelora"
lomab_dir = service_path + "/resources/LoMAB"


attack_config = {'command': "",
'db_ip': "127.0.0.1",
'db_port': 5432,
'db_name': 'postgres',
'db_user': 'postgres',
'db_pass': 'postgres'
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


def argument_parser():
    argument = sys.argv[1]
    base_name, extension = os.path.splitext(argument)

    while True:
        print(f"\033[96m\nvulora\033[0m[\033[91m{base_name}\033[96m]>\033[0m ", end='')
        arg_input = input()

        if arg_input == "help":
            with open(service_path + '/modes/help_messages/direct_sql_injection.txt', 'r') as file:
                file_content = file.read()
                print(file_content)
        elif "command" in arg_input:
            tmp_payload = extract(arg_input, "command")
            attack_config['command'] = tmp_payload
            print(f"\n>> Set argument: command={tmp_payload}")
        elif "db_ip" in arg_input:
            tmp_ip = extract(arg_input, "db_ip")
            if "." in tmp_ip and len(tmp_ip) >= 7:
                attack_config['db_ip'] = tmp_ip
                print(f"\n>> Set argument: db_ip={tmp_ip}")
            else:
                attack_config['db_ip'] = "127.0.0.1"
                print("\n>> Set argument: db_ip='127.0.0.1' (default value, must be a valid IP address)")
        elif "db_port" in arg_input:
            tmp_port = extract(arg_input, "db_port")
            try:
                int_tmp_port = int(tmp_port)
                if 1 <= int_tmp_port <= 65535:
                    attack_config['db_port'] = tmp_port
                    print(f"\n>> Set argument: db_port={tmp_port}")
                else:
                    raise ValueError()
            except ValueError:
                attack_config['db_port'] = 5432
                print("\n>> Set argument: db_port=5432 (default value, database port must be from 1 to 65535)")
        elif "db_name" in arg_input:
            tmp_name = extract(arg_input, "db_name")
            if len(tmp_name) > 0:
                attack_config['db_name'] = tmp_name
                print(f"\n>> Set argument: db_name={tmp_name}")
            else:
                attack_config['db_name'] = "postgres"
                print("\n>> Set argument: db_name=postgres (default value, database name is mandatory)")
        elif "db_user" in arg_input:
            tmp_user = extract(arg_input, "db_user")
            if len(tmp_user) > 0:
                attack_config['db_user'] = tmp_user
                print(f"\n>> Set argument: db_user={tmp_user}")
            else:
                attack_config['db_user'] = "postgres"
                print("\n>> Set argument: db_user=postgres (default value, database username is mandatory)")
        elif "db_pass" in arg_input:
            tmp_pass = extract(arg_input, "db_pass")
            if len(tmp_pass) > 0:
                attack_config['db_pass'] = tmp_pass
                print(f"\n>> Set argument: db_pass={tmp_pass}")
            else:
                attack_config['db_pass'] = "postgres"
                print("\n>> Set argument: db_pass=postgres (default value, database password is mandatory)")
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
    print("\n[INFO]: Starting the SQL injection attack...\n")

    if attack_config['command'] != "":
        subprocess.run(["psql", f"postgresql://{attack_config['db_user']}:{attack_config['db_pass']}@{attack_config['db_ip']}:{attack_config['db_port']}/{attack_config['db_name']}", "-c", attack_config['command']])
    else:
        subprocess.run(["psql", f"postgresql://{attack_config['db_user']}:{attack_config['db_pass']}@{attack_config['db_ip']}:{attack_config['db_port']}/{attack_config['db_name']}"])


if __name__ == "__main__":
    try:
        argument_parser()
        run_attack()
    except KeyboardInterrupt:
        exit(0)

    exit(0)
