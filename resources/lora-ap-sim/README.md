# LoRa@FIIT Access Point and End Nodes simulator
STIoT packet generator which simulates LoRa@FIIT wireless access point and LoRa@FIIT end nodes.

## Supported features and TODO

### LoRa PHY Features
- [X] Generate a position of each node randomly from uniform distribution
- [X] Calculate a PATH LOSS depending on the variable distance from AP
- [X] Move the nodes using a normal speed of a human

### Access Points features

#### LoRa Concentrator Features Support
- [X] Pseudo-random RSSI, SNR generation
- [X] Sending frequency data in STIoT messages
- [X] Support for Command Line Interface (CLI)
- [X] Duty cycle contraints and refresh

#### Thread-safe Features
- [X] Non-blocking socket communication to improve scalability
- [X] Thread-safe message queuing

#### QoS Support
- [X] Emergency message support
- [X] Priority queue for emergency messages

#### Collisions
- [X] Uplink collision simulation
- [X] Downlink collision simulation

### End Nodes Features
- [X] End node duty cycle constraints and refresh
- [X] Processing network data from network server to adapt communication parameters
- [X] Calculate time-on-air (TOA) for each message
- [X] Data retransmission in case of collision
- [X] Support for Upper Confidence Bound parameter selection
- [X] Support for Thompson Sampling parameter selection
- [X] Update parameters based on partial results from Network Server (MABP-case)
- [X] Random initial movement direction

## Command line interface

### End nodes generation is required if data folder is empty
You are free to change these variables in generator.py:
```
file_path="data/group1.txt"
num_of_nodes = 100
```

Then you should run
```
generator.py
```

### Single access point usage
Recommended approach.
Could be displayed by running main.py -h or main.py --help commands
```
main.py -i <access-point-id>

-i <dev_id>, --id=<dev_id> - Specify LoRa AP hardware id

-r, --register - Include end nodes registration process

-s, --shuffle - Shuffle list of end nodes

-f <file_path>, --file=<file_path> - Specify LoRa node id file

-b, --bandit - Activating bandit nodes support

-t, --test - Using test scenario for developing purposes
```

### Multi access point usage
Just run the file. It generates 10x[number of files] new access points.
This usage is buggy and can cause memmory leaks.
Use at your own risk.
```
run.py
```
