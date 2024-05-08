#!/bin/bash

# Check sudo
if [ "$(id -u)" != "0" ]; then
    echo -ne "\n[ERROR]: You need root privileges to run this script.\n"
    exit 1
fi

echo -ne "\nStarting VulneLora installation...\n\n"

# Default vulnelora tool path
tool_path="/opt/vulnelora"

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

# Get device type
cat /sys/firmware/devicetree/base/model > "$tool_path/setup_files/device_info"

# Get rockyou.txt
echo "[INFO]: Downloading rockyou.txt..."
wget -O "$tool_path/resources/rockyou.txt" https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt

if [ $? -eq 0 ]; then
    echo "[SUCCESS]: Download successful."
else
    echo "[FAILED]: Download failed, it is recommended to download the rockyou file manually."
fi

# Get and install LoAP and util_pkt_logger services
echo "[INFO]: Configuring the LoAP service..."
mkdir /opt/lorafiit_forwarder/
cd /opt/lorafiit_forwarder/
git clone https://github.com/loraalex/LoAP.git
mv /opt/lorafiit_forwarder/LoAP/* /opt/lorafiit_forwarder
rm -rf /opt/lorafiit_forwarder/LoAP/
cd /opt/lorafiit_forwarder/PacketConverter/
./install.sh
./install.sh daemon
./board_reset.sh

echo "[INFO]: Configuring the util_pkt_logger tool..."
cd /opt/lorafiit_forwarder/lora_gateway/
make 2>/dev/null

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
