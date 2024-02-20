#!/usr/bin/env python3

import os
import json
import subprocess


service_path = "/opt/vulnelora"
attacks_path = "/opt/vulnelora/attacks"
loaded_attacks = {}


def load_attacks():
    global loaded_attacks
    categories = os.listdir(attacks_path)
    index = 1

    for category in categories:
        print(f"\n--> {category}\n")
        loaded_attacks[f"{category}"] = {}

        files = os.listdir(f"{attacks_path}/{category}")
        files.append('Quit VulneLora.py')

        for file in files:
            if file.endswith('.py'):
                loaded_attacks[f"{category}"][str(index)] = f"{file}"
                no_extension_file = os.path.splitext(file)[0]
                if no_extension_file == "Quit VulneLora":
                    print()
                print(f"\t{str(index)}) {no_extension_file}")
                index = index + 1


def main():
    curr_attack_path = ""
    print("\n>> Available attacks:")
    load_attacks()
    chosen_attack = ""
    print()

    option = input(">> Select the attack number:  ")

    found = False
    for group, attacks_dict in loaded_attacks.items():
        if option in attacks_dict:
            if int(option) == len(attacks_dict):
                exit(0)
            else:
                curr_attack_path = f"{attacks_path}/{group}/{attacks_dict[option]}"
                if os.path.exists(curr_attack_path):
                    print(f"\n[SUCCESS]: Loaded attack: {attacks_dict[option]}\n")
                    chosen_attack = attacks_dict[option]
                    found = True
                    break
                else:
                    print("\n[ERROR]: Selected attack not found.\n")
    if not found:
        print("\n[ERROR]: Attack number not found.\n")
        exit(1)

    subprocess.run(['python3', curr_attack_path, chosen_attack])


with open(service_path + '/modes/intro_messages/interactive_mode.txt', 'r') as file:
    file_content = file.read()
    print(file_content)

try:
    main()
except KeyboardInterrupt:
    print("\n\n[INFO]: VulneLora forced to quit by keyboard interrupt. Bye Bye!\n")
    exit(0)
