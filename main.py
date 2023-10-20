import sys
import time
import datetime
import brainboxes
import json

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import *
from PyQt5 import QtGui

Ui_MainWindow, QtBaseClass = uic.loadUiType("main.ui")

class RemoteRelays(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        with open("config.json", 'r+', encoding='utf-8') as file:
            setup = json.load(file)
            setup["Config"]

        self.device_ip = setup["Config"]["ip"]
        self.txtIP.setText(setup["Config"]["ip"])

        self.brainbox = None
        self.status = [0,0,0,0,0,0,0,0,0,0,0,0]
        self.relays = self.status[0:4]
        print(self.relays)

        self.iconRelayOn = QtGui.QPixmap(r"icons\relayon.png")
        self.iconRelayOff = QtGui.QPixmap(r"icons\relayoff.png")
        #botoes
        self.btnRelay0.clicked.connect(lambda: self.activateRelay(relay=0))
        self.btnRelay1.clicked.connect(lambda: self.activateRelay(relay=1))
        self.btnRelay2.clicked.connect(lambda: self.activateRelay(relay=2))
        self.btnRelay3.clicked.connect(lambda: self.activateRelay(relay=3))

        self.connect()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer_status()
    
    def read_status(self):
        if self.brainbox:            
            rxdata = self.brainbox.command_response(b'@01')
            if rxdata is None:
                current_time = datetime.datetime.now().strftime("%d/%b/%Y %H:%M:%S")
                self.txtLog.append(f"{current_time} - Failed Status Response.\n")
            else:
                try:
                    hex_string = str(rxdata).split("'")[1].split(">")[1]  
                    hex_integer = int(hex_string, 16)
                    binary_string = format(hex_integer, 'b')
                    self.status = [int(digit) for digit in binary_string.zfill(12)]
                    self.relays = self.status[0:4]
                    self.relays.reverse()
                except:
                    current_time = datetime.datetime.now().strftime("%d/%b/%Y %H:%M:%S")
                    self.txtLog.append(f"{current_time} - Error Status Response.\n")

    def activateRelay(self, relay):
        self.read_status()
        msg = f"#01A{relay}0{int(not self.relays[relay])}".encode()
        self.brainbox.command_response(msg)
    
    def save_config(self, key, value):        
        with open('config.json', 'r+', encoding='utf-8') as f:
            setup = json.load(f)
        setup[key].update(value)
        with open('config.json', 'w') as f:
            f.seek(0)
            json.dump(setup, f, indent=4)
            f.truncate()
    
    def reconnect(self):
        self.brainbox = None
        self.connect()

    def update(self):
        if self.brainbox:
            interval = self.boxInterval.currentText().split()[0]
            if round(time.time(),0) % int(interval) == 0:
                self.read_status()
                if self.status[3] == 1:
                    self.btnRelay0.setIcon(QtGui.QIcon(self.iconRelayOn))
                elif self.status[3] == 0:
                    self.btnRelay0.setIcon(QtGui.QIcon(self.iconRelayOff))
                if self.status[2] == 1:
                    self.btnRelay1.setIcon(QtGui.QIcon(self.iconRelayOn))
                elif self.status[2] == 0:
                    self.btnRelay1.setIcon(QtGui.QIcon(self.iconRelayOff))
                if self.status[1] == 1:
                    self.btnRelay2.setIcon(QtGui.QIcon(self.iconRelayOn))
                elif self.status[1] == 0:
                    self.btnRelay2.setIcon(QtGui.QIcon(self.iconRelayOff))
                if self.status[0] == 1:
                    self.btnRelay3.setIcon(QtGui.QIcon(self.iconRelayOn))
                elif self.status[0] == 0:
                    self.btnRelay3.setIcon(QtGui.QIcon(self.iconRelayOff))

    def timer_status(self):
        self.timer.start(1000)
    
    def connect(self):
        self.brainbox = brainboxes.AsciiIo(ipaddr=self.device_ip, port=9500, timeout=1.0)
        if self.brainbox:            
            self.txtName.setText(self.brainbox.command_response(b"$01M").decode()[3::])
    
    def closeEvent(self, event):
        config = {
            "ip": self.txtIP.text()
        }
        self.save_config("Config", config)
        event.accept()        

if __name__ == "__main__":
    main_app = QtWidgets.QApplication(sys.argv)
    window = RemoteRelays()

    window.show()
    sys.exit(main_app.exec_())