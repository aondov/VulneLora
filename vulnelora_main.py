#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os


local_path = "/opt/vulnelora"


def print_line():
	print(50*'_'+'\n')


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
