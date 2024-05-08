# VulneLora
Vulnerability assessment tool for LoRa technology and LoRa@FIIT protocol.

<br>

## [IMPORTANT] Disclaimer
This tool is provided for educational and research purposes only. By accessing or using this tool, you agree to use it responsibly and within the bounds of the law. The creators of this tool are not responsible for any misuse, damage, or unlawful activities conducted with it. Users are reminded that unauthorized access to or disruption of wireless communications networks is illegal in many jurisdictions. It is your responsibility to ensure compliance with all applicable laws, regulations, and ethical guidelines when using this tool. Be aware of the legal implications and obtain appropriate authorization before conducting security assessments on networks that you do not own or manage.

<br>

## Installing VulneLora
Installation process of VulneLora is automatized and requires only a few steps to finish.

Firstly, install required packages:
```
sudo apt update
sudo apt install git python3 postgresql-client dsniff
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

Move all files from cloned directory to your own VulneLora directory and remove the cloned directory:

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

If the installation process is successful, the script will notify you and you can start using the VulneLora tool. If you encounter any errors, try to re-run the script first before examining the error in detail.

<br>

## Usage
VulneLora can be started using following command (and its arguments):

vulnelora [-h] [ -I | -S | -a]

Supported arguments:
- **-h, --help** - Show help message
- **-I** - Run VulneLora in the interactive mode - choose the attack, configure it and run the exploit
- **-S** - Run VulneLora in the simulation mode - configure your own LoRa@FIIT simulation (1 AP and 1-500 end nodes) and test your own scenarios
- **-a** - Add new script for a custom attack

<br>

## Requirements
The device which will be using the VulneLora tool needs to be compatible with following services:
- **packet_converter** - part of the LoRaFIIT repository [3], required to capture LoRa@FIIT messages
- **util_pkt_logger** - part of the LoRaFIIT repository [3], required to capture LoRaWAN messages
- recommended version of Python is **Python 3.9.x**

<br>

## Features
- **main menu** - user can choose between 2 startup modes:
1. Interactive mode
    - user first chooses the attacks from displayed options, then configures the attack using a custom command line, where specific parameters are set via command "*&lt;variable-name&gt; &lt;value&gt;*"
    - program can upload the edited firmware LoMAB [2] to an end device (applied only for some attacks)
    - program can start pre-defined attacks, which exploit several parts of the LoRa@FIIT infrastructure
    - program can save and load the running configuration of the selected attack
2. Simulation mode
    - user runs the *lora-ap-sim* [1] simulator, which simulates LoRa@FIIT gateway and end devices (for testing purposes)
    - user can configure the connection arguments, such as RSSI, SNR, frequency, spreading factor, etc.
    - user can configure a specific IP and port for the LoNES network server
    - user can configure a number of end nodes to be generated and simulated
    - user can save/load a running configuration in json format
- **automatized installation** - VulneLora has its own installation script, which installs the VulneLora tool and prepares all necessary requirements to use it properly
- currently supported attacks include:
    - **Direct SQL injection** - perform the SQLi attack on a specific LoNES [4] network server or LoAP [5] access point
    - **End device SQL injection** - perform the SQLi attack on a specific LoNES [4] network server by uploading a malicious payload to a registered end device
    - **DoS - ARP spoofing** - perform the ARP spoofing attack on a specific network device in the infrastructure (VulneLora must be ran as **SUDO** to perform this attack)
    - **DoS - SETR flood** - send a large amount of SETR messages to flood a network server and possibly perform DoS on it
    - **Eavesdropping** - capture packets flowing through the access point on which the VulneLora is running on
    - **PSK extraction** - extract the PSK value from network server or AP to allow registering of your own end device
    - **Replay attack** - capture register packets flowing through the access point and use data from them to allow your own end device to communicate
    - **SSH exploit** - perform a dictionary brute-force attack on the SSH service located on a network server or access point 
- **custom attack script template** - users can add their own attack for a specific IoT technology and/or protocol by using a template script, which adheres to the pre-defined format of other attack scripts

<br>

## Possible issues

1. *packet_converter* service outputs error "Error checking certificate" - Inside the connection handler source code in Packet Converter service ("*<srv_path>*/lorafiit_forwarder/PacketConverter/src/ConnectionController.cpp"), comment out the following code (should start at **line 61**):

```
if(SSL_get_verify_result(ssl) != X509_V_OK)
{
    std::cerr << "Error checking certificate" << std::endl;
    BIO_free_all(bio);
    SSL_CTX_free(ctx);
    return -1;
}
```
2. *packet_converter* service outputs error "Problem starting network communication" - Make sure your network server IP and port are set correctly in the configuration file of the service. The configuration file is located in "*<srv_path>*/lorafiit_forwarder/PacketConverter/**config.json**"

<br>

## TODO
- [ ] code refactoring
- [ ] correct functionality review

<br>

## Sources
[1] https://github.com/alexandervalach/lora-ap-sim.git

[2] https://github.com/alexandervalach/LoMAB.git

[3] https://github.com/loraalex/LoRaFIIT.git

[4] https://github.com/loraalex/LoNES.git

[5] https://github.com/loraalex/LoAP.git
