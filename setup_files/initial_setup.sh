#!/bin/bash


# Check sudo
if [ "$(id -u)" != "0" ]; then
    echo -ne "\n[ERROR]: You need root privileges to run this script.\n"
    exit 1
fi


echo -ne "\nStarting VulneLora installation...\n\n"


# Required services installation
apt update
services_file="/opt/vulnelora/setup_files/requirements.txt"

if [ ! -f "$services_file" ]; then
    echo "[ERROR]: File $services_file not found. It should be located in the same directory as this script."
    exit 1
fi


# Install required python packages
echo "[INFO]: Installing packages using pip..."
pip install -r "$services_file" --ignore-installed 2>/dev/null
echo "[SUCCESS]: Packages installed successfully."


# Create a platformio binary alias to use it as a basic command
platformio_cmd=$(find / -type f -iwholename "*/bin/platformio*" 2>/dev/null | head -n 1)
if [ -n "$platformio_cmd" ]; then
    echo "alias platformio='$platformio_cmd'" >> ~/.bashrc
    echo "[SUCCESS]: Alias 'platformio' created successfully!"
else
    echo "[ERROR]: Platformio binary not found, it is recommended to create its alias manually in ~/.bashrc."
fi


# Service alias
touch /usr/local/bin/vulnelora
chmod +x /usr/local/bin/vulnelora
echo -ne '#!/bin/bash\npython3 /opt/vulnelora/vulnelora_main.py "$@"' > /usr/local/bin/vulnelora


# Service installation result check
file_path="/usr/local/bin/vulnelora"
err_flag=0

if [ -s "$file_path" ]; then
	echo "[SUCCESS]: VulneLora service has been created successfully!"

	# Check if the file is executable
	if [ -x "$file_path" ]; then
		echo "[SUCCESS]: VulneLora service has executable permissions!"
	else
		echo "[ERROR]: VulneLora service does not have executable permissions. Please, assign them manually in /usr/local/bin/"
		err_flag=1
	fi
else
	if [ -e "$file_path" ]; then
		echo "[ERROR]: VulneLora service file exists but is empty. Try to re-run this script."
	else
		echo "[ERROR]: VulneLora service file does not exist. Try to re-run this script."
	fi
	err_flag=1
fi


if [ "$err_flag" -eq 0 ]; then
	echo "[SUCCESS]: VulneLora installed successfully!"
	exit 0
else
	echo "[FAILED]: VulneLora installation encountered some errors. Try to re-run this script."
	exit 1
fi
