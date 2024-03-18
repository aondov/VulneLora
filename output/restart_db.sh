#!/bin/bash

read -sp "SSH password: " pwd
echo

echo "[INFO]: Clearing and restarting database..."
user=lones
database=lones
format=csv
vulnelora_folder=/opt/vulnelora/output/LoRa@FIIT
rserver=192.168.94.54
ruser=aondov
container_name=postgres_container

sshpass -p "$pwd" ssh -p 22 -q -t $ruser@$rserver "docker exec -it ${container_name} psql -d ${database} -U ${user} -c 'delete from aps cascade;alter sequence aps_dev_id_seq restart with 1;delete from aps_config;alter sequence aps_config_id_seq restart with 1;delete from downlink_messages cascade;alter sequence downlink_messages_id_seq restart with 1;delete from nodes cascade;alter sequence nodes_dev_id_seq restart with 1;delete from uplink_messages cascade;alter sequence uplink_messages_id_seq restart with 1;'"
echo "[SUCCESS]: Database restarted!"
