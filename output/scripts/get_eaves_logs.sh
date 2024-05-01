#!/bin/bash

ruser=lorafiit
rserver=192.168.94.55
vulnelora_folder="/opt/vulnelora/resources"

sshpass -p "$1" scp -q -P 22 $ruser@$rserver:/home/$ruser/eavesdropping_tmp_capture.log $vulnelora_folder/target_eaves_logs.log
