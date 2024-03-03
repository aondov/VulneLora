# LoMAB
LoRa@FIIT Multi-armed Bandit  Firmware for ATmega328P

## End-device installation manual

- Download [Visual Studio Code](https://code.visualstudio.com/)
- Install PlatformIO in Visual Studio Code
- Install necessary extension **atmel-avr** for PlatformIO.
- Install FT232RTL driver for Windows
- Clone repository [LoMAB](https://github.com/alexandervalach/LoMAB)
- Clone repository [LoRa@FIIT](https://github.com/loraalex/LoRaFIIT.git) and copy it into the **lib/** directory in the **LoMAB** repository
- In **"lib/src/lora.h"**, look for the **"MAB_UCB_ENABLED"** and **"CAD_ENABLED"** macros. If needed, set them to 0.
- In **"lib/src/RH_RF95.h"**, look for the **"DEVICE_ID"** macros. Set all of these macros to the hexadecimal value of your end-device. (e.g. if your end-device has device ID set to "E", set all of these macros to "0xEE")
- Connect the LoRa Radio Node to your computer using an FT232RTL USB-to-TTL converter.
- Build the solution to verify that the necessary dependencies are installed. If not, install the missing ones.
- Upload the code to the end-device and start the serial monitor.

&nbsp;

After completing the steps above, your device should connect to the AP, provided you have a working AP with a suitable configuration. Successful connection can be verified by the **"Registration successful, netconfig recieved"** message in the serial monitor.

Another indicator of a successful end-device registration is seeing the application data from your end-device in the **LoRa AP** (LoAP) or **LoRa Network Server** (LoNES) **logs**. These data should be labeled as **"app_data"** and you can list them by issuing the following commands:

- for LoNES, move to the directory where your **LoNES Dockerfile** is, and run the **"docker logs -n 50 *<container_name>*"** command
- for LoAP, use the **"sudo journalctl -u packet_converter -n 50"** command

Application data should be visible in both of these devices, altough you may find them encoded with **base64**. If the *app_data* value is the same as the **appData** value in the **"src/main.cpp"** source code (inside the *loop()* function), your connection is fully functional and your end-device is now ready to send any required data.

## Possible issues

**1. Your MIC throws error**
- If you are seeing the *"Bad MIC"* error, start your diagnostic by verifying that you have the PRESHARED_KEY value set correctly in your **.env** file in LoNES.
- Don't forget to export your *.env* file after every modification.

**2. The registration process keeps failing and restarting**
- Similarly to the previous point, first try to verify the PRESHARED_KEY value.
- If it is set correctly, try to restart the LoNES and LoAP devices.
- Check the log messages on LoNES and LoAP devices and verify that both of your devices are receiving at least some LoRa@FIIT messages. If it does, the connectivity is not an issue.
- If none of these recommendations work, there is a possibility that one of your devices (either LoNES, LoAP, or device) are malfunctioning.

**3. The device upload process failed**
- In case of the upload process failing, analyze the errors shown on the Visual Studio Code command line.
- Since there may be various errors encountered during the upload process, it is difficult to create a universal troubleshooting guide. Try to fix the issue by browsing the Internet and looking for different solutions. 
