#!/bin/bash

read -sp "LoNES SSH password: " pwd
echo
read -sp "LoAP SSH password: " pwd_ap
echo

echo "[INFO]: Retrieving new data from database..."
bash ./scripts/get_data.sh uplink_messages "$pwd"
bash ./scripts/get_data.sh downlink_messages "$pwd"
bash ./scripts/get_data.sh users "$pwd"
bash ./scripts/get_data.sh nodes "$pwd"
bash ./scripts/get_data.sh aps "$pwd"

echo "[INFO]: Retrieving new data from AP..."
bash ./scripts/get_eaves_logs.sh "$pwd_ap"

echo "[SUCCESS]: Data updated!"
