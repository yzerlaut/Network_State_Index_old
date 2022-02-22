import sys, argparse
from PyQt5 import QtGui, QtWidgets, QtCore
from . import gui

parser=argparse.ArgumentParser(description="Network State Index software",
                               formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-f', "--filename", type=str, default='')
args = parser.parse_args()
                
app = QtWidgets.QApplication(sys.argv)
main = gui.Window(app, datafile=args.filename)
sys.exit(app.exec_())


