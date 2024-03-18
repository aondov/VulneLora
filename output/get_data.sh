#!/bin/bash

# Fill in the values
user=lones
database=lones
table=$1
format=csv
vulnelora_folder=/opt/vulnelora/output/LoRa@FIIT
rserver=192.168.94.54
ruser=aondov
container_name=postgres_container

sshpass -p "$2" ssh -p 22 -q -t $ruser@$rserver "docker exec -it ${container_name} psql -d ${database} -U ${user} -c 'COPY (SELECT * FROM ${table}) TO STDOUT ${format} HEADER' > ${table}.${format}"

sshpass -p "$2" scp -q -P 22 $ruser@$rserver:/home/$ruser/$table.$format $vulnelora_folder/$table.$format
