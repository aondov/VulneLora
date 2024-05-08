#!/bin/bash

# Fill in the values
user=admin
database=postgres
table="$1"
format=csv
vulnelora_folder=/opt/vulnelora/output/LoRa@FIIT
rserver="$2"
ruser=admin
container_name=postgres_container

sshpass -p "$3" ssh -p 22 -q -t $ruser@$rserver "docker exec -it ${container_name} psql -d ${database} -U ${user} -c 'COPY (SELECT * FROM ${table}) TO STDOUT ${format} HEADER' > ${table}.${format}"

sshpass -p "$3" scp -q -P 22 $ruser@$rserver:/home/$ruser/$table.$format $vulnelora_folder/$table.$format
