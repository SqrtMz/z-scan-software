import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
import serial.tools.list_ports

class Home(QMainWindow):
    
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.setWindowTitle("Home")

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        quit_action = file_menu.addAction("Quit")
        quit_action.triggered.connect(self.close)

        w = QWidget()
        self.setCentralWidget(w)

        test_btn = QPushButton("Test")
        test_btn.pressed.connect(self.do_shit)

        main_layout = QVBoxLayout()
        main_layout.addWidget(test_btn)

        w.setLayout(main_layout)


    def do_shit(self):
        myports = [tuple(p)[0] for p in list(serial.tools.list_ports.comports())]

        print(myports)