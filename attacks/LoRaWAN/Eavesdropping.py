import os
import sys
import json
import csv
import subprocess
from pathlib import Path


save_flag = 0
service_path = "/opt/vulnelora"
pkt_logger_path = "/opt/vulnelora/resources"


attack_config = {'save_capture': False,
'capture_path': "",
'save_analysis': False,
'analysis_path': ""
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
    print("\n[INFO]: Started collecting logs (stop with Ctrl+c)...\n")

    try:
        command = ['./util_pkt_logger']

        process = subprocess.Popen(command, cwd=pkt_logger_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return_code = process.wait()
    except KeyboardInterrupt:
        print("\n\n[INFO]: Log collection stopped, starting analysis...\n")
        return
    except Exception as e:
        print(f"Error occurred: {str(e)}")


def analyze_logs():
    json_logs = []
    content = ""
    record_counter = 1

    files = os.listdir(pkt_logger_path)
    log_files = [file for file in files if file.startswith("pktlog_")]

    if len(log_files) == 0:
        print("[ERROR]: Possible error with concentrator. Try again, please.")
        return

    curr_logfile = log_files[0]

    with open(f"{pkt_logger_path}/{curr_logfile}", 'r') as file_r:
        content = file_r.readlines()

        if len(content) <= 1:
            print("\n[ERROR]: No data captured, try again")
            os.remove(f"{pkt_logger_path}/{curr_logfile}")
            return

        if attack_config['save_capture']:
            c_logfile = attack_config['capture_path']

            with open(c_logfile, 'w') as clear_file:
                clear_file.write("")

            with open(c_logfile, 'a') as file:
                for line in content:
                    file.write(line)

            print(f"\n[SUCCESS]: Captured data saved successfully in '{c_logfile}'!")

    headers = content[0].split(',')

    for line in content[1:]:
        fields = line.split(',')
        row_data = {header.strip().strip('\"'): field.strip().strip('\"') for header, field in zip(headers, fields)}
        json_logs.append(row_data)

    for log in json_logs:
        json_output = json.dumps(log, indent=4)
        parsed_json = json.loads(json_output)

        print()
        print(20 * '#', end=' ')
        print(f"Message No. {record_counter}", end=' ')
        print(20 * '#')

        try:
            hex_string = parsed_json['payload'][20:38].replace('-','')
            byte_data = bytes.fromhex(hex_string)

            formatted_bytes = ', '.join([f"0x{byte:02x}" for byte in byte_data])
            print(f"\n[INFO]: Possible end device ID: {formatted_bytes}")
        except IndexError:
            print("\n[INFO]: Could not find any possible end device ID.")
        except KeyError:
            print("\n[INFO]: Current message does not include any payload.")
        except Exception as e:
            print(f"[ERROR]: Unexpected error occured: {str(e)}")

        print()
        print(json_output)
        record_counter = record_counter + 1

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

    os.remove(f"{pkt_logger_path}/{curr_logfile}")


def detect_service():
    global pkt_logger_path
    filename = "util_pkt_logger"

    for root, dirs, files in os.walk("/", topdown=True):
        if filename in files:
            file_path = os.path.join(root, filename)
            pkt_logger_path = str(root)
            return True
    return False


def argument_parser():
    argument = sys.argv[1]
    base_name, extension = os.path.splitext(argument)

    while True:
        print(f"\033[96m\nvulora\033[0m[\033[91m{base_name}\033[96m]>\033[0m ", end='')
        arg_input = input()

        if arg_input == "help":
            with open(service_path + '/modes/help_messages/eavesdropping.txt', 'r') as file:
                file_content = file.read()
                print(file_content)
        elif "save_capture" in arg_input:
            if "save_capture true" in arg_input:
                attack_config['save_capture'] = True
                print(f"\n>> Enabled argument: save_capture")
            else:
                attack_config['save_capture'] = False
                print(f"\n>> Disabled argument: save_capture")
        elif "save_analysis" in arg_input:
            if "save_analysis true" in arg_input:
                attack_config['save_analysis'] = True
                print(f"\n>> Enabled argument: save_analysis")
            else:
                attack_config['save_analysis'] = False
                print(f"\n>> Disabled argument: save_analysis")
        elif "capture_path" in arg_input:
            if attack_config['save_capture'] == False:
                print("\n>> [ERROR]: Enable save_capture configuration first using command 'save_capture True'!")
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
                    attack_config['capture_path'] = "./vulora_capture.log"
                    print("\n>> Set argument: capture_path='./vulora_capture.log' (default value, path is not valid)")
        elif "analysis_path" in arg_input:
            if attack_config['save_analysis'] == False:
                print("\n>> [ERROR]: Enable save_analysis configuration first using command 'save_analysis True'!")
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
                    attack_config['analysis_path'] = "./vulora_analysis.log"
                    print("\n>> Set argument: analysis_path='./vulora_analysis.log' (default value, path is not valid)")
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
            print("\n>> [ERROR]: Missing util_pkt_logger service, cannot run this attack")
            exit(1)

        argument_parser()
        collect_logs()
        analyze_logs()
    except KeyboardInterrupt:
        exit(0)

    exit(0)
