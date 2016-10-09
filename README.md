# pyCAR
A Car In-Dash with pure Python3 and qt4 on Raspberry Pi (Jessie). In my case i use the Raspberry Pi 3. 

Including:

- Navit Navigation (Improvements needed)
- Bluetooth HFP and A2DP functionality (both controlled via pyCAR)
- Import of Cellphones Phonebook
- Radio FM-Tuner with si4703 Breakout Board (including RDS)
- MP3-Player in pure Python3
- Use of 7" Touchscreen from Raspberry Pi Foundation
- Bluetooth-Dongle (HFP Capabilities)

No use of 3rd-Party like Kodi. I use a USB Audio Mouse (Hercules Muse Pocket). If you dont need Radio and/or HFP (because of Microfon for HFP and Line-In for Radio) the internal Soundcard should work, too. But there are some configuration needed. I also disabled the internal BT from Raspberry, because it wont work properly. HFP depends on self compiled Pulseaudio (v.6) and ofono.org.

Tuner-Module available here:

http://www.ebay.de/itm/191674482268?_trksid=p2057872.m2749.l2649&ssPageName=STRK%3AMEBIDX%3AIT

Video available on Youtube:

https://www.youtube.com/watch?v=3dzsPGwNwMc

You need a USB-Stick for Music and other pyCAR dependicies (like Phonebooks and Navit Map). There must be the following structure:

pyCar/Music/MyMusicAlbum1/MySong1

pyCar/Music/MyMusicAlbum1/MySong2

pyCar/Music/MyMusicAlbum1/...

pyCar/Music/MyMusicAlbum2/MySong1

pyCar/Music/MyMusicAlbum2/MySong2

pyCar/Music/MyMusicAlbum2/...

pyCar/Music/...

pyCar/navit/map.bin (This is a Map from OSM)

pyCar/Phone/Phonebooks (Here will be the Phonebooks Databases saved)

        
After plugged in the Stick he will be available under /media/pi/pyCar/...

