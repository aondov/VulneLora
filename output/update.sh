#!/bin/bash

read -sp "Input LoNES IP address: " ip
echo
read -sp "Input LoNES SSH password: " pwd
echo
echo
read -sp "Input gateway IP address: " ip_ap
echo
read -sp "Input gateway SSH password: " pwd_ap
echo

echo "[INFO]: Retrieving new data from database..."
bash ./scripts/get_data.sh uplink_messages "$ip" "$pwd"
bash ./scripts/get_data.sh downlink_messages "$ip" "$pwd"
bash ./scripts/get_data.sh users "$ip" "$pwd"
bash ./scripts/get_data.sh aps "$ip" "$pwd"

echo "[INFO]: Retrieving new data from AP..."
bash ./scripts/get_eaves_logs.sh "$ip_ap" "$pwd_ap"

echo "[INFO]: Data updated!"
