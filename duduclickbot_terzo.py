import sys
import os
import asyncio
import threading
import random
import time
import requests
import re
from qasync import QEventLoop
from PyQt5 import QtCore, QtGui, QtWidgets
import pyautogui
from qt_material import apply_stylesheet


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(229, 159)
        MainWindow.setFixedSize(229, 159)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.id_asta = QtWidgets.QLineEdit(self.centralwidget)
        self.id_asta.setGeometry(QtCore.QRect(30, 20, 171, 20))
        self.id_asta.setObjectName("id_asta")
        self.timerslider = QtWidgets.QSlider(self.centralwidget)
        self.timerslider.setGeometry(QtCore.QRect(30, 50, 171, 22))
        self.timerslider.setMinimum(0)
        self.timerslider.setMaximum(15)
        self.timerslider.setValue(1)  # Default a 1 secondo
        self.timerslider.setOrientation(QtCore.Qt.Horizontal)
        self.timerslider.setObjectName("timerslider")
        self.avvia = QtWidgets.QPushButton(self.centralwidget)
        self.avvia.setGeometry(QtCore.QRect(30, 110, 75, 23))
        self.avvia.setObjectName("avvia")
        self.ferma = QtWidgets.QPushButton(self.centralwidget)
        self.ferma.setGeometry(QtCore.QRect(130, 110, 71, 23))
        self.ferma.setObjectName("ferma")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(6, 0, 221, 16))
        self.label.setObjectName("label")
        self.prezzo_min = QtWidgets.QSpinBox(self.centralwidget)
        self.prezzo_min.setGeometry(QtCore.QRect(50, 80, 61, 22))
        self.prezzo_min.setMaximum(9999)
        self.prezzo_min.setObjectName("prezzo_min")
        self.prezzo_max = QtWidgets.QSpinBox(self.centralwidget)
        self.prezzo_max.setGeometry(QtCore.QRect(120, 80, 61, 22))
        self.prezzo_max.setProperty("showGroupSeparator", False)
        self.prezzo_max.setMaximum(9999)
        self.prezzo_max.setStepType(QtWidgets.QAbstractSpinBox.DefaultStepType)
        self.prezzo_max.setDisplayIntegerBase(10)
        self.prezzo_max.setObjectName("prezzo_max")        
        MainWindow.setCentralWidget(self.centralwidget)
        self.alldata = QtWidgets.QStatusBar(MainWindow)
        self.alldata.setObjectName("alldata")
        MainWindow.setStatusBar(self.alldata)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Dudu Click"))
        self.id_asta.setToolTip(_translate("MainWindow", "<html><head/><body><p>ID ASTA</p></body></html>"))
        self.avvia.setText(_translate("MainWindow", "Avvia"))
        self.ferma.setText(_translate("MainWindow", "Ferma"))
        self.label.setText(_translate("MainWindow", "                  github.com/palianitsia"))
        self.prezzo_min.setToolTip(_translate("MainWindow", "<html><head/><body><p>prezzo min</p></body></html>"))
        self.prezzo_max.setToolTip(_translate("MainWindow", "<html><head/><body><p>prezzo max</p></body></html>"))

class AutoClicker(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        apply_stylesheet(
             self, 
            theme='dark_cyan.xml',
            invert_secondary=True,
            extra={
                'density_scale': '-2',
                'font_family': 'Arial',
            }
        )
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.running = False
        self.click_thread = None
        self.mouse_button = 'left'
        self.click_type = 'double'
        self.click_count = float('inf')
        self.interval = 1  # Default a 1 secondo       
        icon_path = "dudubi2oo.png"
        if os.path.exists(icon_path):
            print(f"Icon found at: {icon_path}")
            self.setWindowIcon(QtGui.QIcon(icon_path))
        else:
            print(f"Attenzione: file {icon_path} non trovato")
            print(f"Current working directory: {os.getcwd()}")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.ui.avvia.clicked.connect(self.start_clicking)
        self.ui.ferma.clicked.connect(self.stop_clicking)
        self.ui.timerslider.valueChanged.connect(self.update_slider_display)      
        self.update_slider_display(1)
    
    def update_slider_display(self, value):
        """Update the slider value and show tooltip"""
        self.interval = value
        QtWidgets.QToolTip.showText(
            self.ui.timerslider.mapToGlobal(QtCore.QPoint(0, -30)),
            f"Click a {value} secondi dalla fine",
            self.ui.timerslider,
            QtCore.QRect(),
            2000
        )
        self.ui.alldata.showMessage(f"Timer impostato: {value} secondi")
        print(f"Timer impostato a {value} secondi")
    
    def start_clicking(self):
        if self.running:
            self.ui.alldata.showMessage("Già in esecuzione")
            return     
        auction_id = self.ui.id_asta.text()       
        if not auction_id:
            self.ui.alldata.showMessage("Inserisci ID asta")
            return      
        self.running = True
        self.ui.alldata.showMessage(f"Avviato - Click a {self.interval}s dalla fine")
        print(f"Avvio autoclicker - Click a {self.interval} secondi dalla fine")        
        self.click_thread = threading.Thread(target=self.click_loop, args=(auction_id,), daemon=True)
        self.click_thread.start()
    
    def click_loop(self, auction_id):
        CORREZIONE_TIMER = 0
        count = 0
        same_time_counter = 0
        last_time_left = None
        prezzo_min_raggiunto = False
        same_time_start = None
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1"
        ]
        user_agent_index = 0
        with requests.Session() as s:
            while self.running and count < self.click_count:
                try:
                    headers = {"User-Agent": user_agents[user_agent_index], "Connection": "keep-alive", "Cache-Control": "no-cache", "X-Requested-With": "XMLHttpRequest", "Content-Type": "text/html; charset=UTF-8"}
                    URL = f"https://it.bidoo.com/data.php?ALL={auction_id}&LISTID=0"
                    r = s.get(URL, headers=headers, timeout=(0.2, 0.3))
                    if ";OFF;" in r.text:
                        self.running = False
                        msg = "🛑 Asta conclusa - fermo esecuzione"
                        self.ui.alldata.showMessage(msg)
                        print(msg)
                        break
                    if ";STOP;" in r.text:
                        msg = "⏸️ Asta in pausa - ricontrollo tra 30 secondi"
                        self.ui.alldata.showMessage(msg)
                        print(msg)
                        time.sleep(30)
                        continue
                    if r.status_code == 200:
                        all_data_timer_re = re.findall(r'\(|\)|\d{10}', r.text)
                        if len(all_data_timer_re) >= 2:
                            differenza_secondi = int(all_data_timer_re[1]) - int(all_data_timer_re[0])
                            time_left = differenza_secondi + CORREZIONE_TIMER
                            current_interval = self.ui.timerslider.value()
                            prezzo_min = self.ui.prezzo_min.value()
                            prezzo_max = self.ui.prezzo_max.value()
                            try:
                                prezzo_attuale = int(r.text.split(';')[3]) / 100
                                prezzo_str = f"{prezzo_attuale:.2f}€"
                            except Exception:
                                prezzo_attuale = None
                                prezzo_str = "N/A"
                            if prezzo_attuale is not None and prezzo_max > 0 and prezzo_attuale >= prezzo_max:
                                self.running = False
                                msg = "💰 Prezzo massimo raggiunto - fermo bot"
                                self.ui.alldata.showMessage(msg)
                                print(msg)
                                break
                            if prezzo_min == 0 and prezzo_max == 0:
                                prezzo_min_raggiunto = True
                            elif prezzo_min == 0 and prezzo_attuale > 0:
                                prezzo_min_raggiunto = True
                            elif  prezzo_min > 0 and prezzo_attuale is not None and prezzo_attuale >= prezzo_min:
                                prezzo_min_raggiunto = True
                            else:
                                prezzo_min_raggiunto = False
                            if not prezzo_min_raggiunto:
                                msg = f"⏳ Attendo prezzo min {prezzo_min}€ - Attuale: {prezzo_str} "
                                self.ui.alldata.showMessage(msg)
                                print(msg, end='\r')
                                time.sleep(1)
                                continue
                            if time_left == last_time_left:
                                if same_time_start is None:
                                    same_time_start = time.time()
                                elif time.time() - same_time_start >= 2:
                                    print("⚠️ Tempo invariato per almeno 2 secondi. Cambio User-Agent.")
                                    user_agent_index = (user_agent_index + 1) % len(user_agents)
                                    same_time_start = None
                                    continue
                            else:
                                same_time_start = None
                            last_time_left = time_left
                            status_msg = f"⏱️ Tempo: {time_left}s | Prezzo: {prezzo_str} (click a {current_interval}s)"
                            self.ui.alldata.showMessage(status_msg)
                            print(status_msg, end='\r')
                            if -3 <= differenza_secondi and time_left <= current_interval:
                                x = random.randint(1001, 1150)
                                y = random.randint(480, 520)
                                pyautogui.click(x, y, button=self.mouse_button, clicks=2)
                                count += 1
                                click_msg = f"🖱️ Click #{count} a {x},{y} - Tempo: {time_left}s"
                                self.ui.alldata.showMessage(click_msg)
                                print(click_msg)
                                time.sleep(0.5)
                    else:
                        print(f"❌ Errore HTTP: {r.status_code}")
                        time.sleep(1)
                except Exception as e:
                    error_msg = f"⚠️ Errore: {e}"
                    self.ui.alldata.showMessage(error_msg)
                    print(error_msg)
                    time.sleep(1)
        self.running = False
        self.ui.alldata.showMessage("✅ Pronto")
        print("✅ Autoclicker fermato")
   
    def stop_clicking(self):
        if not self.running:
            self.ui.alldata.showMessage("Non in esecuzione")
            return
        self.running = False
        self.ui.alldata.showMessage("Fermatura in corso...")
        print("🔁 Richiesta fermatura autoclicker")
        self.ui.id_asta.clear()
        self.ui.prezzo_min.setValue(0)
        self.ui.prezzo_max.setValue(0)
        print("🧹 Parametri azzerati (ID asta, prezzo min/max)")
        self.ui.alldata.showMessage("🔁 Inserisci nuovi dati.")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    clicker = AutoClicker()
    clicker.show()
    
    with loop:
        loop.run_forever()