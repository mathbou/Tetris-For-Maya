from PySide2.QtWidgets import *
from PySide2.QtCore import *

class Ui(QWidget):
    def __init__(self, controller, name, parent=None):
        QWidget.__init__(self, parent)
        self.controller = controller
        #  create window
        self.setWindowTitle(name)
        self.setMinimumWidth(150)
        self.move(75,175)
        self.setWindowFlags(Qt.Window)
        self.action = 0

        # create widgets

        title_lbl = QLabel("Tetris for maya")
        self.start_btn = QPushButton("Start game")

        # create layout

        main_layout = QVBoxLayout()

        # connect layout

        main_layout.addWidget(title_lbl)
        main_layout.addWidget(self.start_btn)

        self.setLayout(main_layout)
        # connect widget

        self.start_btn.clicked.connect(self.start_game)

    def start_game(self):
        self.controller.start_game()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            print "up"
            self.action = 1
        elif event.key() == Qt.Key_Down:
            print "down"
            self.action = 2
        elif event.key() == Qt.Key_Left:
            print "left"
            self.action = 3
        elif event.key() == Qt.Key_Right:
            print "right"
            self.action = 4