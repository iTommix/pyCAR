---
typora-root-url: ../pyCAR
---

# pyCAR
### A Car In-Dash with pure Python3, qt4, Pulseaudio, ofono on Raspberry Pi.

![Splash-Screen](/install/splash.png)

### My Hardware-Configuration:

- Raspberry Pi 3B+, Raspios buster
- Soundcard WM8960-Audio-HAT [1]
- Radio Tuner SI4703 (I2C-Controlled) [2]
- 2 x Amplifer MAX9744 (Rear/Front, I2C-Controlled) [3]
- 7" Touchscreen from Raspberry Pi Foundation [4]
- Bluetooth-Dongle instead of Built-In BT
- GPS-Mouse u-blox 6 [5]

### Features:

- Navit Turn-By-Turn Navigation
- Bluetooth HFP and A2DP functionality
- Import of Cellphones Phonebook
- Radio FM-Tuner with SI4703 or Web-Radio (Auto-Detect)
- MP3-Player based on mplayer in pure Python3
- Module-Based. You can develope own Modules

No use of 3rd-Party like Kodi. 

I disabled the internal BT from Raspberry, because it wont work properly.

### Install:

1. Write a fresh Raspios on a SD-Card (2020-05-27-raspios-buster-armhf.img)
2. After first boot configure localizations and timezone with raspi-config, reboot.
3. Clone this repository to your RPi <code>git clone https://github.com/iTommix/pyCAR.git</code>
4. Change to the install folder <code>cd pyCAR/install</code>
5. Execute the Installscript <code>./install.sh</code>
6. At first select 'Install Base-System'

The Scripts will uninstall not needed programs, update the System and install needed programs as well. You will be forced to reboot the Pi several times. Please follow the instructions from the Installscript.

After install the Base-System, you can choose an Audio-Option:

1. WM8960-Audio-HAT
2. Google Voice-Hat (experimental)
3. RPi's Built-In BCM2835 (nothing will be changed)

### Prepare USB-Stick for Data and Music
We will use a USB-Stick to hold the Music and some Data to prevent excessive writing on the SD-Card. The structure should be:

![USB-Stick](/install/screenshots/folders.png?raw=true "The Structure of the USB-Stick")

As you can see, the Stick is named pyCar and got the folders 'Music', 'navit', 'phone' and 'Radio'. The file stations.xml is only for Webradio. In the folder Music put your mp3-Files. Each album as a own folder. In the folder 'navit' will be the map (e.g. from OpenStreetMap) as .bin-File and an optional SpeedCam.txt ;-)

### Disclaimer
You can use this project as it is. pyCAR is still under development. 


[1] https://www.amazon.de/Waveshare-WM8960-Audio-HAT-Raspberry/dp/B07KN8424G

[2] https://www.amazon.de/Breakout-Board-Si4703-Tuner-Funkmodul/dp/B017JZCJG6

[3] https://www.reichelt.de/entwicklerboards-audioverstaerker-stereo-20-w-klasse-d-max9-debo-sound-amp3-p235512.html?PROVID=2788&&r=1

[4] https://www.amazon.de/Raspberry-Pi-7-Inch-Screen-Display/dp/B014WKCFR4

[5] https://www.reichelt.de/gps-galileo-empfaenger-u-blox-6-navilock-61840-p135559.html
