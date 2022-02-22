import sys
from PyQt5 import QtWidgets

from . import gui

app = QtWidgets.QApplication(sys.argv)
main = gui.Window(app)
sys.exit(app.exec_())
