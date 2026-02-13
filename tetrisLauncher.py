import shiboken2
import maya.OpenMayaUI as mui

import tetrisController, tetrisUi
reload(tetrisController)
reload(tetrisUi)

from tetrisController import Controller
from tetrisUi import Ui
from PySide2 import QtWidgets


if __name__ == '__main__':
    # define names
    window_title = "Link Bones"
    # get maya window
    ptr = mui.MQtUtil.mainWindow()
    parent = shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget)

    # create window
    window = Controller(Ui, "Tetris", parent)
    window.show()
