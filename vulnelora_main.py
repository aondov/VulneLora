#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os
import shutil


local_path = "/opt/vulnelora"


def print_line():
	print(50*'_'+'\n')


def path_exists(tech, file_name):
	if os.path.exists(f"{local_path}/attacks/{tech}"):
		if os.path.exists(f"{local_path}/attacks/{tech}/{file_name}.py"):
			return os.path.getsize(f"{local_path}/attacks/{tech}/{file_name}.py") > 0
	return False


def argument_parser(help_only):
	class CustomHelpFormatter(argparse.HelpFormatter):
		def _format_usage(self, usage, actions, groups, prefix):
			usage = super()._format_usage(usage, actions, groups, prefix)
			return usage.replace('vulnelora_main.py', 'vulnelora')

	# Initialize the parser
	parser = argparse.ArgumentParser(description='Vulnerability assessment tool for LoRa technology and LoRa@FIIT protocol.', formatter_class=CustomHelpFormatter)

	group = parser.add_mutually_exclusive_group()

	# Add arguments
	group.add_argument('-I', action='store_true', help='Run VulneLora in the interactive mode')
	group.add_argument('-S', action='store_true', help='Run VulneLora in the simulated mode')
	group.add_argument('-a', action='store_true', help='Add a new attack to VulneLora')
	parser.add_argument('-run', nargs='?', help=argparse.SUPPRESS)

	if help_only:
		parser.print_help()
	else:

		# Parse the arguments
		args, unknown_args = parser.parse_known_args()

		try:
			# Check and handle specified options
			if args.I:
				if not args.run:
					subprocess.run(['python3', local_path + '/modes/vulnelora_interactive.py'])
				else:
					subprocess.run(['python3', args.run])
			if args.S:
				if args.run:
					command = "python3 " + local_path + "/resources/lora-ap-sim/src/main.py"
					conf_args = ''.join(args.run)
					command = command + " " + conf_args
					subprocess.run(command, shell=True)
				else:
					subprocess.run(['python3', local_path + '/modes/vulnelora_simulation.py'])
			if args.a:
				technology = input("Enter name of the technology: ")
				name = input("Enter name of your attack: ")
				if not path_exists(technology, name):
					os.makedirs(f"{local_path}/attacks/{technology}")
					shutil.copyfile(f"{local_path}/resources/script_wizard/template.py", f"{local_path}/attacks/{technology}/{name}.py")
					subprocess.run(["nano", f"{local_path}/attacks/{technology}/{name}.py"])
				else:
					print(f"[ERROR]: Attack '{name}' already exists. Please, EDIT the existing one or REMOVE it to proceed.")
					exit(1)
			if unknown_args:
				print(f"Error: Unrecognized argument(s): {' '.join(unknown_args)}\n")
		except KeyboardInterrupt:
			exit(0)


# Read and print the contents of the text file
print_line()

with open(local_path + '/logo/vulnelora_ascii_logo.txt', 'r') as file:
    file_content = file.read()
    print(file_content)

print_line()

if len(sys.argv) > 1:
	argument_parser(False)
else:
	argument_parser(True)
