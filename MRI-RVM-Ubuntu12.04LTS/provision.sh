#!/bin/bash

########################
#
# Run this against Ubuntu 12.04 LTS 64bit
#
########################

echo "Type the ip address or CNAME of the remote server, followed by [ENTER]:"

read ip_address

echo "==========> setup_server"
fab -H root@$ip_address setup_server

echo "==========> ssh-keygen for TODO"
fab -H TODO@$ip_address create_ssh_key

echo "==========> ssh-keygen for TODO-name_of_app"
fab -H TODO-name_of_app@$ip_address create_ssh_key
