#!/bin/bash

read -sp "SSH password: " pwd
echo

echo "[INFO]: Retrieving new data from database..."
bash ./get_data.sh uplink_messages "$pwd"
bash ./get_data.sh downlink_messages "$pwd"
bash ./get_data.sh users "$pwd"
bash ./get_data.sh nodes "$pwd"
bash ./get_data.sh aps "$pwd"
echo "[SUCCESS]: Data updated!"
