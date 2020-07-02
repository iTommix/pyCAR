# pyCAR
A Car In-Dash with pure Python3, qt4, Pulseaudio, ofono on Raspberry Pi (buster).

My Hardware-Configuration:
- Raspberry Pi 3B+
- Soundcard WM8960-Audio-HAT [1]
- Radio Tuner SI4703 [2]
- 2 x Amplifer MAX9744 (Rear/Front) [3]
- 7" Touchscreen from Raspberry Pi Foundation [4]
- Bluetooth-Dongle instead of Built-In BT
- GPS-Mouse u-blox 6 [5]

Features:

- Navit Navigation
- Bluetooth HFP and A2DP functionality
- Import of Cellphones Phonebook
- Radio FM-Tuner with si4703 or Web-Radio
- MP3-Player based on mplayer in pure Python3

No use of 3rd-Party like Kodi. I disabled the internal BT from Raspberry, because it wont work properly.

Install:

1. Write a fresh Raspios on a SD-Card
2. After first boot configure localizations and timezone, reboot.




[1] https://www.amazon.de/Waveshare-WM8960-Audio-HAT-Raspberry/dp/B07KN8424G

[2] https://www.amazon.de/Breakout-Board-Si4703-Tuner-Funkmodul/dp/B017JZCJG6

[3] https://www.reichelt.de/entwicklerboards-audioverstaerker-stereo-20-w-klasse-d-max9-debo-sound-amp3-p235512.html?PROVID=2788&&r=1

[4] https://www.amazon.de/Raspberry-Pi-7-Inch-Screen-Display/dp/B014WKCFR4

[5] https://www.reichelt.de/gps-galileo-empfaenger-u-blox-6-navilock-61840-p135559.html
