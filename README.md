# pyCAR
A Car In-Dash build with pure Python3 and qt4 on Raspberry Pi

Including:

- Navit Navigation
- Bluetooth HFP and A2DP functionality
- Radio FM-Tuner with si4703 Breakout Board
- MP3-Player in pure Python3
- Use of 7" Touchscreen from Raspberry Pi Foundation

No use of 3rd-Party like Kodi.

HFP depends on self compiled Pulseaudio (v. 6) and ofono.org.

Tuner-Module Available here:

http://www.ebay.de/itm/191674482268?_trksid=p2057872.m2749.l2649&ssPageName=STRK%3AMEBIDX%3AIT

Video available on Youtube (a bit old, new one comes soon):

https://www.youtube.com/watch?v=nsZiFj6lNYA

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

