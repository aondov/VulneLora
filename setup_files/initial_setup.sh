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

while IFS= read -r service; do
    apt install "$service"
done < "$services_file"


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
