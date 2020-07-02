# pyCAR
## A Car In-Dash with pure Python3, qt4, Pulseaudio, ofono on Raspberry Pi (buster).

### My Hardware-Configuration:
- Raspberry Pi 3B+
- Soundcard WM8960-Audio-HAT [1]
- Radio Tuner SI4703 [2]
- 2 x Amplifer MAX9744 (Rear/Front) [3]
- 7" Touchscreen from Raspberry Pi Foundation [4]
- Bluetooth-Dongle instead of Built-In BT
- GPS-Mouse u-blox 6 [5]

### Features:

- Navit Navigation
- Bluetooth HFP and A2DP functionality
- Import of Cellphones Phonebook
- Radio FM-Tuner with SI4703 or Web-Radio (Auto-Detect)
- MP3-Player based on mplayer in pure Python3
- Module-Based. You can develope own Modules

No use of 3rd-Party like Kodi. I disabled the internal BT from Raspberry, because it wont work properly.

### Install:

1. Write a fresh Raspios on a SD-Card
2. After first boot configure localizations and timezone, reboot.
3. Clone this repository to your RPi <code>git clone https://github.com/iTommix/pyCAR.git</code>
4. Rename the repository <code>mv pyCAR install</code>
5. Change to the folder <code>cd install</code>
6. Execute the Installscript <code>./install.sh</code>
7. At first select 'Install Base-System'

The Scripts will uninstall not needed programs, update the System and install needed programs as well. You will be forced to reboot the Pi several times. Please follow the instructions from the Installscript.

After install the Base-System, you can choose an Audio-Option:

1. WM8960-Audio-HAT
2. Google Voice-Hat (experimental)
3. RPi's Built-In BCM2835

### Prepare USB-Stick for Data and Music
We will use a USB-Stick to hold the Music and some Data to prevent excessive writing on the SD-Card. The structure should be
<code>
└── pyCar<br />
    ├── Music<br /> 
    ├── navit<br />
    │   ├── D-A-CH.bin<br />
    │   └── SpeedCamText.txt<br />
    ├── Phone<br />
    │   └── Phonebooks<br />
    │       └── 3C_2E_FF_1D_93_41.db<br />
    └── Radio<br />
        └── stations.xml<br />
</code>

### Disclaimer
You can use this project as it is. pyCAR is still under development. 


[1] https://www.amazon.de/Waveshare-WM8960-Audio-HAT-Raspberry/dp/B07KN8424G

[2] https://www.amazon.de/Breakout-Board-Si4703-Tuner-Funkmodul/dp/B017JZCJG6

[3] https://www.reichelt.de/entwicklerboards-audioverstaerker-stereo-20-w-klasse-d-max9-debo-sound-amp3-p235512.html?PROVID=2788&&r=1

[4] https://www.amazon.de/Raspberry-Pi-7-Inch-Screen-Display/dp/B014WKCFR4

[5] https://www.reichelt.de/gps-galileo-empfaenger-u-blox-6-navilock-61840-p135559.html
