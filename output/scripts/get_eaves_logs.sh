#!/bin/bash

ruser=admin
rserver="$1"
vulnelora_folder="/opt/vulnelora/resources"

sshpass -p "$2" scp -q -P 22 $ruser@$rserver:/home/$ruser/eavesdropping_tmp_capture.log $vulnelora_folder/target_eaves_logs.log
