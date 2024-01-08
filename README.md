# VulneLora
Vulnerability assessment tool for LoRa technology and LoRa@FIIT protocol.

## Installing VulneLora

Installation process of VulneLora is automatized and requires only few steps to finish.

Firstly, install "git" and "python3":
```
sudo apt update
sudo apt install git python3
```

Create a directory in "/opt" and set the owner of this directory to the current user:
```
sudo mkdir /opt/vulnelora
sudo chown $USER:$USER /opt/vulnelora
```

Enter newly created directory and clone VulneLora repository in there:
```
cd /opt/vulnelora
git clone https://github.com/aondov/VulneLora.git
```

Run initial_setup.sh script in setup_scripts directory:
```
cd setup_scripts/
chmod +x initial_setup.sh
./initial_setup.sh
```
