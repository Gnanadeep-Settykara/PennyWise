# Dependencies 
import sys
from PySide6.QtCore import Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QMainWindow, QHeaderView, QHBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, 
                               QWidget)

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("PennyWise")
   
        #Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        #Exit the QAction
        exit_action = QAction("Exit",self)
        exit_action.setShortcut("Ctrl+Q")


if __name__ == '__main__':
    # Qt Application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()

    #Execute application
    sys.exit(app.exec())