import sys
from PySide6.QtWidgets import QApplication
from home.home import Home

app = QApplication(sys.argv)

w = Home(app)
w.resize(1280, 720)
w.show()

if __name__ == "__main__":
    sys.exit(app.exec())