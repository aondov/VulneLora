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

Move all files from cloned directory to own VulneLora directory and remove the cloned directory:

***Note**: Be very careful when using the "rm -rf" command, as it can permanently delete files and/or directories which are given as an argument.*
```
mv /opt/vulnelora/VulneLora/* /opt/vulnelora
rm -rf /opt/vulnelora/VulneLora
```

Run *initial_setup.sh* script in the *setup_files/* directory:
```
cd /opt/vulnelora/setup_files/
chmod +x initial_setup.sh
sudo ./initial_setup.sh
```

If the installation process is successful, the script will notify you and you can start using the VulneLora tool. If you encounter any errors, try to re-run the script first, before examining the error in detail.

## Usage
VulneLora can be started using following command (and its arguments):

vulnelora [-h] [ -G | -S | -C ]

Optional arguments:
- **-h, --help** - Show help message and exit
- **-G** - Run VulneLora in the interactive mode
- **-S** - Run VulneLora in the simulation mode
- **-C** - Run VulneLora in the command line mode

## Features
- **main menu** - user can choose between 3 startup modes:
1. Interactive mode - user configures the attacks using simple GUI, where specific parameters are set via command "*SET &lt;variable-name&gt; = &lt;value&gt;*"
2. Simulation mode
  - user runs the *lora-ap-sim* [1] simulator, which simulates LoRa@FIIT gateway and end devices (for testing purposes)
  - user can configure the connection arguments, such as RSSI, SNR, frequency, spreading factor, etc.
  - user can configure a specific IP and port for the LoNES network server
  - user can configure a number of end nodes to be generated and simulated
  - user can save/load a running configuration in json format
3. Command line mode - user configures the attacks using traditional command line arguments and runs the attack as so called "one-liner"
- **automatized installation** - VulneLora has its own installation script, which installs the VulneLora tool and prepares all necessary requirements to use it properly

## TODO
- [ ] code every startup mode and test it
- [x] integrate *lora-ap-sim* [1] to VulneLora
- [ ] implement the attacks on LoRa and LoRa@FIIT, regardless of the startup mode
- [ ] create testing scenarios (acceptance tests)
- [ ] test the attacks, evaluate their results

## Sources
[1] https://github.com/alexandervalach/lora-ap-sim.git
