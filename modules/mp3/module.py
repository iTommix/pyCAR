"""
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import QIcon, QImage, QPixmap, QPalette, QBrush
from PyQt4.QtCore import Qt
"""

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap, QPalette, QBrush
from PyQt5 import QtWidgets, QtCore

import mplayer, sys, os, json, time, asyncio, mutagen, io, random
from mutagen import File
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from PIL import Image
from PIL import ImageFilter
from subprocess import call

path=os.path.dirname(os.path.abspath( __file__ )).rsplit('/', 1)
music={}



class mp3(QtWidgets.QMainWindow):

    def __init__(self, parent=None, settings=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.mp3player = mplayer.Player()
        self.playTimer = QtCore.QTimer()
        self.playTimer.timeout.connect(lambda: self.setSlider())
        

    def loaded(self):
        # setup buttons
        """
        self.btn_Interprets.clicked.connect(lambda: self.selectList("interprets"))
        self.btn_Album.clicked.connect(lambda: self.selectList("alben"))
        self.musicSlider.sliderReleased.connect(self.setPosition)
        self.albumList.itemClicked.connect(lambda: self.getSongs())
        self.musicList.itemClicked.connect(lambda: self.newSong())
        """
        self.btn_Like.clicked.connect(lambda: self.like())
        self.btn_Repeat.clicked.connect(lambda: self.setRepeat())
        self.btn_Shuffle.clicked.connect(lambda: self.setShuffle())
        self.btn_Shuffle_list.clicked.connect(lambda: self.setShuffle())
        
        self.btn_Select.clicked.connect(lambda: self.parent.setPage(self.stack, 1))
        
        self.albumList.itemClicked.connect(lambda: self.getSongs())
        self.musicList.itemClicked.connect(lambda: self.selectAlbum())
        
        self.albumList.setVerticalScrollMode(self.albumList.ScrollPerPixel)
        self.musicList.setVerticalScrollMode(self.musicList.ScrollPerPixel)
        
        QtWidgets.QScroller.grabGesture(self.albumList.viewport(), QtWidgets.QScroller.LeftMouseButtonGesture)
        QtWidgets.QScroller.grabGesture(self.musicList.viewport(), QtWidgets.QScroller.LeftMouseButtonGesture)
        
        self.musicList.verticalScrollBar().setStyleSheet("QScrollBar:vertical {width:0px}");
        self.albumList.verticalScrollBar().setStyleSheet("QScrollBar:vertical {width:0px}");
        
        self.btn_Play.clicked.connect(lambda: self.togglePlay())
        self.btn_Backward.clicked.connect(lambda: self.previous())
        self.btn_Forward.clicked.connect(lambda: self.next())
        
        
        self.musicSlider.sliderReleased.connect(lambda: self.getSlider())
        self.musicSlider.valueChanged.connect(lambda: self.getSliderPos())
        

    def ready(self): 
        self.usbPath = self.parent.modules["setup"]["instance"].settings["usb"]+"/Music"
        self.getAlbums()

    def focus(self):
        pass
    
    def play(self):
        if self.settings["album"] !="" and os.path.isdir(self.usbPath+"/"+self.settings["album"]):
            if self.settings["shuffle"]:
                self.btn_Shuffle.setStyleSheet("background-image: url(./images/shuffle.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 2px solid #e42659;background-position: center")
            song = music[self.settings["album"]][self.settings["song"]]
            self.lbl_Artist.setText(song["artist"])
            self.lbl_Album.setText(song["album"])
            self.lbl_Title.setText(song["title"])
            self.parent.setInfo(song["artist"], song["title"])
            self.mp3player.loadfile(song["path"])
            self.mp3player.time_pos = self.settings["position"]
            self.musicSlider.setValue(int(self.settings["position"]))
            self.playTimer.start(1000)
            self.btn_Play.setStyleSheet("background-image: url(./images/pause.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")
            self.btn_Like.setStyleSheet("background-image: url(./images/like_"+song["like"]+".png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")
            try:
                self.lbl_Time_left.setText(self.parent.getSongLength(self.mp3player.length-self.mp3player.time_pos))
                self.lbl_Time_pos.setText(self.parent.getSongLength(self.mp3player.time_pos))
                self.musicSlider.setMaximum(int(self.mp3player.length)+1)
            except:
                pass
            self.setBackground()
        
    
    def pause(self):
        self.mp3player.stop()
        self.playTimer.stop()
        self.btn_Play.setStyleSheet("background-image: url(./images/play.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")
            
    def stop(self):
        self.pause()
    
    #################################
    # Module related functions      #
    #################################
    
    def next(self):
        if self.settings["song"] < len(music[self.settings["album"]]):
            self.musicList.setCurrentRow(self.settings["song"]+1)
            self.playSong(self.settings["song"]+1)
    
    def previous(self):
        if self.settings["song"] >0:
            self.musicList.setCurrentRow(self.settings["song"]-1)
            self.playSong(self.settings["song"]-1)
    
    def togglePlay(self):
        if self.mp3player.filename == None:
            print("play")
            self.play()
        else:
            self.pause()
            
            
    def setShuffle(self):
        if self.settings["shuffle"]==0:     
            self.settings["shuffle"]=1
            if self.stack.currentIndex()>0:
                start=0
                self.settings["shuffleList"] = random.sample(range(start, len(music[self.settings["album"]])), (len(music[self.settings["album"]])-start))
                self.playSong(self.settings["shuffleList"][0])
                self.parent.setPage(self.stack, 0)
                del self.settings["shuffleList"][0]
            else:
                start=self.settings["song"]+1
                self.settings["shuffleList"] = random.sample(range(start, len(music[self.settings["album"]])), (len(music[self.settings["album"]])-start))
            self.btn_Shuffle.setStyleSheet("background-image: url(./images/shuffle.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 2px solid #e42659;background-position: center")
        else:
            self.settings["shuffle"]=0
            self.settings["shuffleList"]=[]
            self.btn_Shuffle.setStyleSheet("background-image: url(./images/shuffle.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border:0px;background-position: center")   
    
    def setRepeat(self):
        if self.settings["shuffle"]==1:
            self.setShuffle()
        if self.lbl_Title.text() != "":
            if self.settings["repeat"]==0:
                self.settings["repeat"]=1
                self.btn_Repeat.setStyleSheet("background-image: url(./images/repeat1.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")
            elif self.settings["repeat"]==1:
                self.settings["repeat"]=2
                self.btn_Repeat.setStyleSheet("background-image: url(./images/repeat.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 2px solid #e42659;background-position: center")
            else:
                self.settings["repeat"]=0
                self.btn_Repeat.setStyleSheet("background-image: url(./images/repeat.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")

    
    def like(self):
        song = music[self.settings["album"]][self.settings["song"]]["path"]
        like = not int(music[self.settings["album"]][self.settings["song"]]["like"] == "True")
        music[self.settings["album"]][self.settings["song"]]["like"] = str(like)
        self.btn_Like.setStyleSheet("background-image: url(./images/like_"+str(like)+".png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")
        if(song.lower().endswith(".mp3")):
            tags = ID3(song)
            tags.add(mutagen.id3.TXXX(encoding=3, desc=u'like', text=str(like)))
            tags.save(song)
        else:
            tags = MP4(song)
            tags["----:TXXX:like"] = bytes(like, 'UTF-8')
            tags.save(song)
    
    #################################
    # Player related functions      #
    #################################
    def selectAlbum(self):
        self.settings["album"]=self.albumList.currentItem().text()
        self.playSong(self.musicList.currentRow())
        self.settings["shuffle"]=0
        self.settings["repeat"]=0
        self.settings["shuffleList"]=[]
        self.btn_Repeat.setStyleSheet("background-image: url(./images/repeat.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")
        self.btn_Shuffle.setStyleSheet("background-image: url(./images/shuffle.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border:0px;background-position: center")
        self.parent.setPage(self.stack, 0)
        
    #######################################################
    # Start a song from current album by given songnumber #
    #######################################################
    def playSong(self, songNumber):
        self.settings["song"]=songNumber
        song = music[self.settings["album"]][songNumber]
        self.lbl_Artist.setText(song["artist"])
        self.lbl_Album.setText(song["album"])
        self.lbl_Title.setText(song["title"])
        self.parent.setInfo(song["artist"], song["title"])
        self.btn_Like.setStyleSheet("background-image: url(./images/like_"+song["like"]+".png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")
        self.musicSlider.setValue(0)
        self.setBackground()
        self.mp3player.loadfile(song["path"])
        self.musicSlider.setMaximum(int(self.mp3player.length)+1)
        self.btn_Play.setStyleSheet("background-image: url(./images/pause.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")
        #self.parent.setPage(self.stack, 0)
        self.playTimer.start(1000)
    
    def getSlider(self):
        self.mp3player.time_pos = self.musicSlider.value()
        
    def getSliderPos(self):
        self.lbl_Time_left.setText(self.parent.getSongLength(self.musicSlider.maximum()-self.musicSlider.value()))
        self.lbl_Time_pos.setText(self.parent.getSongLength(self.musicSlider.value()))
        
    ################################################
    # Set the slider according to position of song #
    # and start new one at the end of the song     #
    ################################################
    def setSlider(self):
        #if int(self.mp3player.time_pos) >= int(self.mp3player.length):
        if self.mp3player.filename is None:
        #if self.musicSlider.value() == self.musicSlider.maximum():
            self.musicSlider.setValue(0)
            print("END")
            self.settings["position"]=0
            if self.settings["shuffle"]==1:
                if len(self.settings["shuffleList"]) > 0:
                    self.musicList.setCurrentRow(self.settings["shuffleList"][0])
                    self.playSong(self.settings["shuffleList"][0])
                    del self.settings["shuffleList"][0]
                    print(self.settings["shuffleList"])
                else:
                    self.settings["shuffleList"]=[]
                    self.clearLabels()
            elif self.settings["repeat"]==0:
                print(self.settings["song"], " => ", len(music[self.settings["album"]]))
                if self.settings["song"] < len(music[self.settings["album"]])-1:
                    self.musicList.setCurrentRow(self.settings["song"]+1)
                    self.playSong(self.settings["song"]+1)
                else:
                    self.clearLabels()
                    self.playTimer.stop()
                    self.btn_Play.setStyleSheet("background-image: url(./images/play.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")
                    self.settings["song"]=0
            else:
                if self.settings["repeat"]==1:
                    self.settings["repeat"]=0
                    self.btn_Repeat.setStyleSheet("background-image: url(./images/repeat.png);background-repeat: none; background-color: #eeeeee; border-radius: 5px; border: 0px;background-position: center")
                self.playSong(self.settings["song"])
        else:
            try:
                self.musicSlider.setValue(int(self.mp3player.time_pos))
                self.settings["position"]=int(self.mp3player.time_pos)
            except:
                pass
    
    ########################################
    # Clears the labels if no song to play #
    ########################################
    def clearLabels(self):
        self.parent.setInfo("", "")
        self.lbl_Artist.setText("")
        self.lbl_Album.setText("")
        self.lbl_Title.setText("")
        pixmap = QPixmap()
        self.backgroundImage.setPixmap(pixmap)
        
    ###################################
    # Get a Backgroundimage from Song #
    ###################################
    def setBackground(self):
        try: 
            source = Image.open(self.usbPath+"/"+self.settings["album"]+"/.covers/"+str(self.settings["song"])+".jpg")
            source=source.filter(ImageFilter.GaussianBlur(4))
            if source.width<700:
                width=700
                height=int(width * (source.height / source.width))
                source = source.resize((width, height), Image.ANTIALIAS)
                top = int((height - 480)/2)
                bottom = int(height-top)
                box=[0,top,700,bottom]
                source=source.crop(box)
            elif source.height<480:
                pass
            else:
                left = int((source.width - 700)/2)
                right = int(source.width-left)
                top = int((source.height - 480)/2)
                bottom = int(source.height-top)
                box=[left,top,right,bottom]
                source=source.crop(box)
            
            ### Bild dunkler machen ###
            im = source.split()
            R, G, B = 0, 1, 2
            constant = 1.5 # constant by which each pixel is divided
            Red = im[R].point(lambda i: i/constant)
            Green = im[G].point(lambda i: i/constant)
            Blue = im[B].point(lambda i: i/constant)
            source = Image.merge(source.mode, (Red, Green, Blue))
    
            
            imgByteArr = io.BytesIO()
            source.save(imgByteArr, format='JPEG')
            image = imgByteArr.getvalue()
            pixmap = QPixmap()
            pixmap.loadFromData(image, "JPEG", Qt.AutoColor)
            self.backgroundImage.setPixmap(pixmap)
    
        except:
            pixmap = QPixmap()
            self.backgroundImage.setPixmap(pixmap)

    

    #################################
    # Display songs from a Album    #
    #################################
    def getSongs(self):
        album = self.albumList.currentItem().text()
        self.lbl_currentAlbum.setText(album);
        self.musicList.clear()
        self.musicList.clearSelection()
        for item in music[album]:
            itm = QtWidgets.QListWidgetItem(music[album][item]["title"]);
            if not os.path.isdir(self.usbPath+"/"+album+"/.covers"):
                os.mkdir(self.usbPath+"/"+album+"/.covers", 777 )
            image = self.usbPath+"/"+album+"/.covers/"+str(item)+".jpg"
            if not os.path.isfile(image):  
                file = File(music[album][item]["path"]) # mutagen can automatically detect format and type of tags
                try:
                    artwork = file.tags['APIC:'].data # access APIC frame and grab the image
                    new = QImage()
                    new.loadFromData(artwork)
                    pixmap = QPixmap(new).scaledToHeight(500, Qt.SmoothTransformation)
                    pixmap.save(image, "JPG")
                except:
                    image=r"./images/nocover.png"
            itm.setIcon(QIcon(image))
            itm.setSelected(False)
            self.musicList.addItem(itm);
        if album == self.settings["album"]:
            self.musicList.setCurrentRow(self.settings["song"])
        self.parent.setPage(self.stack, 2)

    #################################
    # Get all Albums in path        #
    #################################
    def getAlbums(self):
        self.albumList.clear()
        self.albumList.clearSelection()
        albums = self.getFileList(self.usbPath)
        select = -1
        z=0
        for album in albums:
            if album == self.settings["album"]:
                select = z
            music[album]={}
            f=0
            files = self.getFileList(self.usbPath, album)
            for audio in files:
                audio = self.usbPath+"/"+album+"/"+audio
                m = File(audio)
                hr={"TIT2": "title", "TPE1": "artist", "TALB": "album", "TXXX:like": "like"}
                music[album][f] = {}
                for tag in ('TIT2', 'TPE1', 'TALB', 'TXXX:like'): #('title', 'artist', 'album'):
                    try:
                        music[album][f][hr[tag]] = str(m[tag])
                    except:
                        if tag=="TIT2": music[album][f]["title"] = audio
                        if tag=="TPE1": music[album][f]["artist"] = "Unknown"
                        if tag=="TALB": music[album][f]["album"] = album
                        if tag=="TXXX:like": music[album][f]["like"] = "False"

                music[album][f]["path"]=audio
                music[album][f]["played"]=0
                f+=1
            itm = QtWidgets.QListWidgetItem(album);
            itm.setIcon(QIcon(r""+path[0]+"/images/folder.png"));
            z+=1
            self.albumList.addItem(itm);
        if select > -1:
            self.albumList.setCurrentRow(select)

    #################################
    # Get contents of path          #
    #################################
    def getFileList(self, path, folder=""):
        # remove hidden files (i.e. ".thumb")
        path = os.path.join(path, folder)
        raw_list = filter(lambda element: not element.startswith('.'), os.listdir(path))
        if folder == "":
            return raw_list

        # mp3 and wav files only list
        file_list = filter(lambda element: element.endswith('.mp3') | element.endswith('.m4a'), raw_list)       
        return file_list

    
