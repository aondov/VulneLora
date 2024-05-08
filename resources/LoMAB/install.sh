
#!/bin/bash
set -e

# Define the service location
service_location="/lib/systemd/system/"

check_root() {
    if [ "$UID" != 0 ]; then
        echo "ERROR: Not a root user."
        exit 1
    fi
}

install_default() {
    echo "INFO: Locally installing to this folder:"
    mkdir -p debug
    cd ./debug
    cmake ..
    make
    make install
    cd ..
    echo "SUCCESS: Default installation completed."
}

install_daemon() {
    if [ "$#" -lt 2 ]; then
        service_name="packet_converter"
    else
        service_name="$2"
    fi

    echo "INFO: Installing daemon service: $service_name"
    touch "$service_location/$service_name.service"
    echo "[Unit]" > "$service_location/$service_name.service"
    echo "Description=$service_name daemon" >> "$service_location/$service_name.service"
    echo "[Service]" >> "$service_location/$service_name.service"
    echo "WorkingDirectory=$(pwd)" >> "$service_location/$service_name.service"
    echo "ExecStart=$(pwd)/start.sh" >> "$service_location/$service_name.service"
    echo "SyslogIdentifier=$service_name" >> "$service_location/$service_name.service"
    echo "Restart=always" >> "$service_location/$service_name.service"
    echo "RestartSec=5" >> "$service_location/$service_name.service"
    echo "[Install]" >> "$service_location/$service_name.service"
    echo "WantedBy=multi-user.target" >> "$service_location/$service_name.service"
    systemctl daemon-reload
    systemctl enable "$service_name.service"
    echo "SUCCESS: Service $service_name successfully installed and is located at $service_location/$service_name.service"
    echo "INFO: To disable it, run as super user:"
    echo "  systemctl disable $service_name.service"
}

clear_installation() {
    if [ "$#" -lt 2 ]; then
        service_name="packet_converter"
    else
        service_name="$2"
    fi

    echo "INFO: Clearing all install files for $service_name:"
    rm -f ./packet_converter
    rm -rf ./debug/
    systemctl disable "$service_name.service"
    rm "$service_location/$service_name.service"
    echo "SUCCESS: All $service_name files are cleaned, and systemd daemon is disabled."
}

# Check root user
check_root

# Set what to do
action="default"
if [ "$#" -ge 1 ]; then
    if [ "$1" == "daemon" ] || [ "$1" == "clear" ]; then
        action="$1"
    fi
fi

# Perform the selected action
if [ "$action" == "default" ]; then
    install_default
elif [ "$action" == "daemon" ]; then
    install_daemon "$@"
elif [ "$action" == "clear" ]; then
    clear_installation "$@"
fi
