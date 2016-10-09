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

https://www.amazon.de/Breakout-Board-Si4703-FM-Tuner-Radio-Arduino/dp/B017JZCJG6/ref=pd_lutyp_simh_1_1?ie=UTF8&pd_rd_i=B017JZCJG6&pd_rd_r=6K7BAEC6NGHVQZ615T1X&pd_rd_w=NIOTh&pd_rd_wg=EdvnH&psc=1&refRID=6K7BAEC6NGHVQZ615T1X

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

