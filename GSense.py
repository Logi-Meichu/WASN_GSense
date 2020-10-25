# -*- coding: utf-8 -*-
import pyautogui
import socket, traceback
import xml.etree.ElementTree as ET
import re
import sys
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton


class WorkThread(QThread):
    trigger = pyqtSignal(str)

    def __int__(self):
        super(SocketThread, self).__init__()
       
    def run(self):
        wearing = True 
        preWearingStat = True
        host = '172.20.10.2'
        port = 8089

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.s.bind((host, port))
        print("Success binding")
        
        while 1:
            
            #Get message
            message, address = self.s.recvfrom(8192)
            messageString = message.decode("utf-8")
            
            #Parse xml data
            messageString = "<header>" + re.sub('<\?xml.*\?>', '', messageString) + "</header>" #Remove declaration
            tree = ET.fromstring(messageString)
            
            preWearingStat = wearing    #Save the prestep
            if  float(tree[1][2].text) > 7.0:   # Gravity x: (1, 0) y: (1, 1) z: (1, 2)
                print(float(tree[1][2].text))
                wearing = True
            else:
                wearing = False
                    
            if wearing != preWearingStat:
                pyautogui.hotkey('alt', 'p')    #Continue or stop the record
            
            if wearing:    
                pyautogui.hotkey('alt', 'x')    #Change to headset
            else:
                pyautogui.hotkey('alt', 'z')    #Change to default audi
            
            time.sleep(0.5)
            
    def close(self):
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
                    
class MyMainForm(QMainWindow):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.resize(400,400)
        
        self.work = []
        
        self.btStart = QPushButton(self)
        self.btStart.setText("Start")         
        self.btStart.clicked.connect(self.execute)
        self.btStart.move(150,100)
        
        self.btStop = QPushButton(self)
        self.btStop.setText("Stop")         
        self.btStop.clicked.connect(self.kill)
        self.btStop.move(150,200)
        self.socket_running = False

    def execute(self):
        if not self.socket_running:
            self.work.append(WorkThread())
            socket_array_len = len(self.work) - 1
            self.work[socket_array_len].start()
            self.socket_running = True
        
    def kill(self):
        if self.socket_running:
            socket_array_len = len(self.work) - 1
            self.work[socket_array_len].close()
            self.work[socket_array_len].terminate()
            self.socket_running = False
        
    def display(self,str):
        self.listWidget.addItem(str)
                
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainForm()
    myWin.show()
    sys.exit(app.exec_())