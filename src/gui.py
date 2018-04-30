import sys, os
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pylab as plt
plt.style.use('ggplot')
from PyQt5 import QtGui, QtWidgets, QtCore
import numpy as np
# from analyze_datafile import plot_data, load_data_and_initialize, save_as_npz
# from IO.files_manip import get_files_with_given_exts, rename_files_for_easy_sorting
# from graphs.my_graph import make_multipanel_fig
# from automated_analysis import analysis_window
# from IO.load_data import load_file, get_metadata

FONTSIZE= 5
matplotlib.rcParams.update({'axes.labelsize': FONTSIZE,
                            'axes.titlesize': FONTSIZE,
                            'figure.titlesize': FONTSIZE,
                            'font.size': FONTSIZE,
                            'legend.fontsize': FONTSIZE,
                            'xtick.labelsize': FONTSIZE,
                            'ytick.labelsize': FONTSIZE,
                            'figure.facecolor': 'none',
                            'legend.facecolor': 'none',
                            'axes.facecolor': 'none',
                            'savefig.facecolor': 'none'})

def create_plot_window(parent, hspace=0.01, left=0.05, right=0.99):

    width, height = parent.screensize[0]/1.1, parent.screensize[1]/2.
    
    fig_large_view, AX_large_view = plt.subplots(3, 1, figsize=(7,2))
    plt.subplots_adjust(hspace=hspace, left=left, right=right)
    for i in range(3):
        if i<2:
            AX_large_view[i].set_xticklabels([])

    fig_zoom, AX_zoom  = plt.subplots(3, 1, figsize=(7,3))
    plt.subplots_adjust(hspace=hspace, left=left, right=right)
    for i in range(3):
        if i<2:
            AX_zoom[i].set_xticklabels([])
            
    # # get all figures with their size !
    
    # Window size choosen appropriately
    window = QtWidgets.QDialog()
    # window.setGeometry(100, 150, width, height)
    window.setGeometry(10, 150, width, height)
    
    # this is the Canvas Widget that displays the `figure`
    # it takes the `figure` instance as a parameter to __init__
    canvas_large_view = FigureCanvas(fig_large_view)
    canvas_zoom = FigureCanvas(fig_zoom)
    layout = QtWidgets.QGridLayout(window)

    layout.addWidget(canvas_large_view)
    layout.addWidget(canvas_zoom)
        
    window.setLayout(layout)
            
    return window, AX_large_view, AX_zoom

# def get_list_of_files(cdir="/tmp"):
#     return get_files_with_given_exts(cdir)
        
class Window(QtWidgets.QMainWindow):
    
    def __init__(self, app, parent=None, DATA_LIST=None, KEYS=None):
        
        super(Window, self).__init__(parent)
        
        # buttons and functions
        LABELS = ["q) Quit", "o) Open File"]
        FUNCTIONS = [self.close_app, self.file_open]
        button_length = 113.
        self.setWindowIcon(QtGui.QIcon('pics/logo.png'))
        self.setWindowTitle('Computing the Network State Index')
        self.setGeometry(50, 50, button_length*(1+len(LABELS)), 60)
        
        mainMenu = self.menuBar()
        self.fileMenu = mainMenu.addMenu('&File')
        
        screen = app.primaryScreen()
        rect = screen.availableGeometry()
        self.screensize = rect.width(), rect.height()

        for func, label, shift in zip(FUNCTIONS, LABELS,\
                                      button_length*np.arange(len(LABELS))):
            btn = QtWidgets.QPushButton(label, self)
            btn.clicked.connect(func)
            btn.setMinimumWidth(button_length)
            btn.move(shift, 0)
            action = QtWidgets.QAction(label, self)
            action.setShortcut(label.split(')')[0])
            action.triggered.connect(func)
            self.fileMenu.addAction(action)

        
        self.i_plot, self.analysis_flag = 0, False
        self.FolderAnalysisMenu =  None
        self.FIG_LIST, self.args, self.window2, self.window3, self.params = [], {}, None, None, {}
        self.analysis_flag = False
        self.data = None # DICTIONARY STORING THE DATA !
        try:
            self.filename,self.folder,btn_state = np.load('program_data/last_datafile.npy')
            if btn_state=='False': self.btn.setChecked(False)
            self.FILE_LIST = get_list_of_files(self.folder)
            self.i_plot = np.argwhere(self.FILE_LIST==self.filename)[0][0]
            load_data_and_initialize(self)
            self.update_plot()    
        except (FileNotFoundError, ValueError, IndexError, TypeError):
            self.filename, self.folder = '', ''
            self.statusBar().showMessage('Provide a datafile of a folder for analysis ')
            # self.folder = '/tmp/' # TO be Changed for Cross-Platform implementation !!
            # self.FILE_LIST = get_list_of_files(self.folder)
            # self.filename = self.FILE_LIST[self.i_plot]
            # self.update_plot()
            
        self.window, self.AX_large_view, self.AX_zoom = create_plot_window(self)
        self.window.show()    
        self.show()

    # def set_analysis_folder(self):
    #     if self.btn.isChecked():
    #         self.analysis_folder = os.path.join(os.path.expanduser("~"),'Desktop')
    #         try: self.FolderAnalysisMenu.hide()
    #         except AttributeError: pass
    #     else:
    #         self.analysis_folder = os.path.join(self.folder,'analysis')
    #         self.FolderAnalysisMenu =  analysis_window.FolderAnalysisMenu(self)
    #     if not os.path.exists(self.analysis_folder):
    #         os.makedirs(self.analysis_folder)
    #     print('analysis folder for now: ', self.analysis_folder)
            
    # def analyze(self):
    #     self.analysis_flag = True
    #     self.statusBar().showMessage('Analyzing data [...]')
    #     self.update_plot()    
    #     return 0
    
    # def update_plot(self):
    #     try:
    #         self.FIG_LIST = plot_data(self)
    #     except ValueError:
    #         self.statusBar().showMessage('PROBLEM with datafile : '+\
    #                                      self.filename+', Check It Manually !!')
    #     self.window, self.window3 = create_window(self, self.FIG_LIST,
    #                                               with_toolbar=self.analysis_flag)
    #     self.window.show()
    #     if self.window3 is not None:
    #         self.window3.show()
    #     self.statusBar().showMessage('DATA file : '+self.filename)
    #     self.activateWindow()
        
    # def update_params_and_windows(self):
    #     load_data_and_initialize(self)
    #     self.update_plot()
        
    def close_app(self):
        # if self.filename!='':
        #     np.save('program_data/last_datafile.npy', [self.filename, self.folder, self.btn.isChecked()])
        sys.exit()

    def file_open(self):
        name=QtWidgets.QFileDialog.getOpenFileName(self, 'Open File',\
                                                   self.folder)
        self.analysis_flag = False
        if self.FolderAnalysisMenu is not None:
            self.FolderAnalysisMenu.close()
        try:
            self.filename = name[0]
            load_data_and_initialize(self)
            self.folder = os.path.dirname(self.filename)
            self.set_analysis_folder()
            self.FILE_LIST = get_list_of_files(self.folder)
            self.i_plot = np.argwhere(self.FILE_LIST==self.filename)[0][0]
            self.update_params_and_windows()
        except FileNotFoundError:
            self.statusBar().showMessage('/!\ No datafile found... ')
            # pass

    def folder_open(self):
        name=QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder', self.folder)
        if name!='':
            self.folder = name
        else:
            self.folder = os.path.sep+'tmp'
        self.analysis_flag = False
        try:
            rename_files_for_easy_sorting(dir=self.folder)
            # we first rename the files (add 0, so that '23_01_13' instead of '23_1_13')
            self.set_analysis_folder()
            self.i_plot = 0
            self.FILE_LIST = get_list_of_files(self.folder)
            self.filename = self.FILE_LIST[self.i_plot]
            self.update_params_and_windows()
        except (IndexError, FileNotFoundError, NoneType, OSError):
            self.statusBar().showMessage('/!\ No datafile found... ')
            
    def save_as_data(self):
        i=1
        while os.path.isfile(os.path.join(self.analysis_folder, 'data'+str(i)+'.npz')):
            i+=1
        save_as_npz(self, os.path.join(self.analysis_folder, 'data'+str(i)+'.npz'))
        self.statusBar().showMessage('Saving as : '+os.path.join(self.analysis_folder, 'data'+str(i)+'.npz'))


if __name__ == '__main__':
    import time
    app = QtWidgets.QApplication(sys.argv)
    main = Window(app)
    # main.show()
    sys.exit(app.exec_())
