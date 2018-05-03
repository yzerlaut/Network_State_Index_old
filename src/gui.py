import sys, os, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from src.functions import * # all functions required to make the analysis
from src.IO import * # module to load data, including electrophysiogical recordings

# then modules for GUI
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pylab as plt
plt.style.use('ggplot')
from PyQt5 import QtGui, QtWidgets, QtCore
from matplotlib.widgets import RectangleSelector
import datetime

FONTSIZE= 5
matplotlib.rcParams.update({'axes.labelsize': FONTSIZE,
                            'axes.titlesize': FONTSIZE,
                            'figure.titlesize': FONTSIZE,
                            'font.size': FONTSIZE,
                            'xtick.labelsize': FONTSIZE,
                            'ytick.labelsize': FONTSIZE})


DEFAULT_VALUES = {'alpha':2.85,
                  'Tstate':200,
                  'dt':0.1,
                  'gain':1000.,
                  'Tsmooth':42.,
                  'Tsubsampling':5.,
                  'p0_percentile':1.,
                  'Root_freq':92.,
                  'Band_Factor':1.8,
                  'N_wavelets':10,
                  'xlim':[0,50]}

class Window(QtWidgets.QMainWindow):
    
    def __init__(self, app, parent=None, DATA_LIST=None, KEYS=None):
        
        super(Window, self).__init__(parent)
        
        # buttons and functions
        LABELS = ["q) Quit", "o) Open File", "r) Run analysis", "s) Save Results", "Zoom1", "Zoom2", "Reset Settings"]
        FUNCTIONS = [self.close_app, self.file_open, self.analyze, self.save_results,\
                     self.zoom1, self.zoom2, self.reset_program_settings]
        button_length = 130
        self.setWindowTitle('Computing the Network State Index')
        self.setGeometry(50, 50, button_length*(0.5+len(LABELS)), 180)
        
        mainMenu = self.menuBar()
        self.fileMenu = mainMenu.addMenu('&File')

        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('...')
        
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

        self.window,\
            self.AX_large_view, self.AX_zoom,\
            self.canvas_large_view, self.canvas_zoom = create_plot_window(self)

        self.data = {} # initialized to empty data
        # program defaults
        self.params = DEFAULT_VALUES
        # try:
        #     self.params = dict(np.load('data/last_params.npz'))
        # except (FileNotFoundError, ValueError, IndexError, TypeError):
        #     self.params = {'xlim':[0,50]}
        # data initializaton
        
        ## ------------ Recording and Analysis parameters ----------- ##
        set_recording_params(self, y0=30)
        set_analysis_params(self, y0=90)
        
        self.filename, self.folder = 'data/sample_data.npz', 'data/'
        self.window.show()    
        self.show()
        
        # self.load_data(self.filename)
        # self.large_scale_plot()
        # self.zoom_plot()

    def zoom1(self):
        self.statusBar.showMessage('Draw a rectangle in the TOP plot to set a new zoom')
        self.rs=RectangleSelector(self.AX_large_view, self.onselect,
                             drawtype='box',
                             rectprops = dict(facecolor='red', edgecolor = 'black', alpha=0.5, fill=True))
        
    def zoom2(self):
        self.statusBar.showMessage('Draw a rectangle in the "BOTTOM-Vext" plot to set a new zoom')
        self.rs=RectangleSelector(self.AX_zoom[0], self.onselect,
                             drawtype='box',
                             rectprops = dict(facecolor='red', edgecolor = 'black', alpha=0.5, fill=True))
        
    def onselect(self, eclick, erelease):
        self.params['xlim'] = [min([eclick.xdata, erelease.xdata]), max([eclick.xdata, erelease.xdata])]
        self.zoom_plot()
        
    def load_data(self, filename):
        self.statusBar.showMessage('loading data [...]')
        self.data = load_formatted_data(filename) # see function in src/IO.py
        self.Vext_key = self.data['Channel_Keys'][0] # first key by default
        self.dt = self.data['dt']
        self.nsamples = len(self.set_acq_gain.value()*self.data[self.Vext_key])
        self.filename_textbox.setText('Filename: '+self.filename)
        self.statusBar.showMessage('Data loaded, now "Run Analysis"')
        
    def large_scale_plot(self, Nplot=2000):
        """
        We plot everything on a single axis,
        [10, 20] is Vext
        [0, 10] is pLFP
        [-10, 0] is NSI
        """
        while len(self.AX_large_view.lines)>0:
            del self.AX_large_view.lines[-1] # removing the previous plot
        # large scale version

        if (self.Vext_key in self.data) and ('dt' in self.data):
            lfp_to_plot = self.data[self.Vext_key][::int(self.nsamples/Nplot)]
            ymin, ymax, ymean = np.min(lfp_to_plot), np.max(lfp_to_plot), np.mean(lfp_to_plot)
            scaling = 10./(ymax-ymin)
            self.AX_large_view.plot(np.arange(len(lfp_to_plot))*self.data['dt']*int(self.nsamples/Nplot),
                                    (lfp_to_plot-ymean)*scaling+15., lw=0.5, color=Grey)
            self.AX_large_view.set_xlim([0, self.data['dt']*self.nsamples])
            self.canvas_large_view.draw()
        else:
            self.statusBar.showMessage('No data available [...]')

    def large_scale_plot_NSI(self, Nplot=2000):
        
        # large scale version
        Nsamples = len(self.data['pLFP'])
        plfp_to_plot = self.data['pLFP'][::int(Nsamples/Nplot)]

        ymin, ymax, ymean = np.min(plfp_to_plot), np.max(plfp_to_plot), np.mean(plfp_to_plot)
        scaling = 10./(ymax-ymin)
        self.AX_large_view.plot(np.arange(len(plfp_to_plot))*self.data['new_dt']*int(Nsamples/Nplot),
                                (plfp_to_plot-ymean)*scaling+5., lw=0.5, color=Brown)

        y = self.data['NSI'][self.data['NSI_validated']]
        ymin, ymax, ymean = np.min(y), np.max(y), np.mean(y)
        scaling = 10./(ymax-ymin)
        cond1 = self.data['NSI_validated'] & (self.data['NSI']>0)
        self.AX_large_view.plot(self.data['new_t'][cond1], (self.data['NSI'][cond1]-ymean)*scaling-5.,'.',ms=0.2, color=Kaki)
        cond2 = self.data['NSI_validated'] & (self.data['NSI']<=0)
        self.AX_large_view.plot(self.data['new_t'][cond2],(self.data['NSI'][cond2]-ymean)*scaling-5.,'.',ms=0.2, color=Purple)
        self.canvas_large_view.draw()
        
    def zoom_plot(self, Nplot=2000):

        # cleaning up the plot before:
        for ax in self.AX_zoom:
            while len(ax.lines)>0:
                del ax.lines[-1] # removing the previous plots
            while len(ax.collections)>0:
                del ax.collections[-1] # removing the previous plots

                
        if ((self.Vext_key in self.data) and ('dt' in self.data)):
            i1, i2 = int(self.params['xlim'][0]/self.data['dt']), int(self.params['xlim'][1]/self.data['dt'])
            isubsampling = max([1,int((i2-i1)/Nplot)])
            lfp_to_plot = self.set_acq_gain.value()*self.data[self.Vext_key][i1:i2][::isubsampling]
            self.AX_zoom[0].plot(np.arange(len(lfp_to_plot))*self.data['dt']*isubsampling+self.params['xlim'][0],
                                 lfp_to_plot, lw=0.5, color=Grey)
            y1, y2 = np.min(lfp_to_plot), np.max(lfp_to_plot)
            self.AX_zoom[0].set_ylim([y1-0.05*(y2-y1), y2+0.05*(y2-y1)])
        else:
            self.statusBar.showMessage('No data available [...]')

        if ('pLFP' in self.data):
            
            i1, i2 = int(self.params['xlim'][0]/self.data['new_dt']), int(self.params['xlim'][1]/self.data['new_dt'])
            # plotting pLFP variations
            isubsampling = max([1,int((i2-i1)/Nplot)])
            plfp_to_plot = self.data['pLFP'][i1:i2][::isubsampling]
            self.AX_zoom[1].plot(np.arange(len(plfp_to_plot))*self.data['new_dt']*isubsampling+self.params['xlim'][0],
                                 plfp_to_plot, lw=1, color=Brown)
            y1, y2 = np.min(plfp_to_plot), np.max(plfp_to_plot)
            self.AX_zoom[1].set_ylim([y1-0.05*(y2-y1), y2+0.05*(y2-y1)])
            
            # plotting NSI variations
            nsi_to_plot = self.data['NSI'][i1:i2][::isubsampling]
            self.AX_zoom[2].plot(np.arange(len(plfp_to_plot))*self.data['new_dt']*isubsampling+self.params['xlim'][0],
                                 nsi_to_plot, lw=0.5, color='k')
            self.AX_zoom[2].plot(self.params['xlim'], [0,0], '--', lw=0.1, color='k')
            # self.AX_zoom[2].set_ylim([np.min(plfp_to_plot), np.max(plfp_to_plot)])

            # plotting validated NSI
            cond = self.data['NSI_validated'] &\
                   (self.data['new_t']>self.params['xlim'][0]) &\
                   (self.data['new_t']<=self.params['xlim'][1])
            self.AX_zoom[2].plot(self.data['new_t'][cond & (self.data['NSI']>0)],
                                 self.data['NSI'][cond & (self.data['NSI']>0)], 'o',
                                 ms=1, color=Kaki)
            self.AX_zoom[2].plot(self.data['new_t'][cond & (self.data['NSI']<=0)],
                                 self.data['NSI'][cond & (self.data['NSI']<=0)], 'o',
                                 ms=1, color=Purple)
            self.AX_zoom[1].plot(self.params['xlim'], self.data['p0']*np.ones(2), '--', lw=0.1, color=Brown)
            

        for ax in self.AX_zoom:
            ax.set_xlim(self.params['xlim'])
            
        self.canvas_zoom.draw()

        # highlighting zoom area in the large plot
        if ((self.Vext_key in self.data) and ('dt' in self.data)):
            i1, i2 = int(self.params['xlim'][0]/self.data['dt']), int(self.params['xlim'][1]/self.data['dt'])
            while len(self.AX_large_view.collections)>0:
                del self.AX_large_view.collections[-1] # removing the previous highlight !
            self.AX_large_view.fill_between([i1*self.data['dt'], i2*self.data['dt']], [-10,-10], [20,20], color='r', alpha=.2, lw=0)
            self.AX_large_view.set_ylim([-10,20])
            self.canvas_large_view.draw()
        else:
            self.statusBar.showMessage('No data available [...]')
        
    def analyze(self):
        self.statusBar.showMessage("Analyzing data [...]")
        f0, w0 = self.set_rootfreq.value(), self.set_bandfactor.value()
        preprocess_LFP(self.data,
                       gain = self.set_acq_gain.value(),
                       Vext_key=self.Vext_key,
                       freqs = np.linspace(f0/w0, f0*w0, self.set_N_wvlts.value()), 
                       # percentile_for_p0=self.set_p0_percentile.value()/100.,                   
                       new_dt = self.set_subsampling.value()*1e-3,
                       smoothing=self.set_Tsmooth.value()*1e-3)
        compute_Network_State_Index(self.data,
                                    Tstate=self.set_Tstate.value()*1e-3,
                                    T_sliding_mean=2.*self.set_Tstate.value()*1e-3,
                                    alpha=self.set_alpha.value())
        # now updating plots
        self.large_scale_plot_NSI()
        self.zoom_plot()
        self.statusBar.showMessage("Data Analyzed !")
    
    def file_open(self):
        name=QtWidgets.QFileDialog.getOpenFileName(self, 'Open File',\
                                                   self.folder)
        try:
            self.filename = name[0]
            self.folder = os.path.dirname(self.filename)
            self.load_data(self.filename)
            self.update_keys()
            self.large_scale_plot()
            self.zoom_plot()
            self.statusBar.showMessage('Data succesfully loaded !')
        except FileNotFoundError:
            self.statusBar.showMessage('/!\ No datafile found... ')
            
    def update_keys(self):
        self.set_acq_channel.clear() # delete all items from comboBox
        self.set_acq_channel.addItems(self.data['Channel_Keys'])
        self.set_acq_channel.update()

    def channel_change(self):
        self.Vext_key = self.set_acq_channel.currentText()
        self.large_scale_plot()
        self.zoom_plot()
        
    def close_app(self):
        if self.params is not None:
            np.savez('data/last_params.npz', **self.params)
        sys.exit()
        
    def save_results(self):
        if 'NSI' in self.data:
            results_filename = '.'.join(self.filename.split('.')[:-1]) if '.' in self.filename else self.filename
            results_filename += '_NSI_'+datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')+'.h5'
            print(self.data.keys())
            to_save = {'validated_times': self.data['new_t'][self.data['NSI_validated']],
                       'validated_NSI':self.data['NSI'][self.data['NSI_validated']]}
            save_dict_to_hdf5(to_save, results_filename)
            self.statusBar.showMessage('Results of analysis saved as : '+results_filename)
        else:
            self.statusBar.showMessage('Need to perform analysis first...')

    def reset_program_settings(self):
        self.params = {'xlim':[0,50]}
        self.set_acq_dt.setValue(DEFAULT_VALUES['dt'])
        self.set_acq_gain.setValue(DEFAULT_VALUES['gain'])
        self.set_Tstate.setValue(DEFAULT_VALUES['Tstate'])
        self.set_alpha.setValue(DEFAULT_VALUES['alpha'])
        
    
def create_plot_window(parent, x0=10, y0=250, hspace=0.1, left=0.08, right=0.99, bottom=0.2, figsize=(8,3)):

    width, height = parent.screensize[0]/1.1, parent.screensize[1]/1.5
    
    fig_large_view, AX_large_view = plt.subplots(1, figsize=(figsize[0], figsize[1]/1.5))
    plt.subplots_adjust(hspace=hspace, left=left, right=right, bottom=1.5*bottom)
    AX_large_view.set_xlabel('time (s)')
    AX_large_view.set_yticks([])
    AX_large_view.set_ylim([-10, 20])
        
    fig_zoom, AX_zoom  = plt.subplots(3, 1, figsize=(figsize[0], figsize[1]))
    plt.subplots_adjust(hspace=hspace, left=left, right=right, bottom=bottom)
    AX_zoom[0].set_xticklabels([])
    AX_zoom[1].set_xticklabels([])
    AX_zoom[2].set_xlabel('time (s)')
            
    for ax2, label in zip(AX_zoom, ['$V_{ext}$ ($\mu$V)', 'pLFP ($\mu$V)', 'NSI ($\mu$V)']):
        ax2.set_ylabel(label)
    for x, col, label in zip([0.75, 0.55, 0.35], [Grey, Brown, 'k'],
                             ['$V_{ext}$', 'pLFP', 'NSI']):
        AX_large_view.annotate(label, (0.03, x), color=col, xycoords='figure fraction')
        
    # Window size choosen appropriately
    window = QtWidgets.QDialog()
    window.setGeometry(x0, y0, width, height)

    # this is the Canvas Widget that displays the `figure`
    # it takes the `figure` instance as a parameter to __init__
    
    canvas_large_view = FigureCanvas(fig_large_view)
    canvas_zoom = FigureCanvas(fig_zoom)

    layout = QtWidgets.QGridLayout(window)
    layout.addWidget(canvas_large_view)
    layout.addWidget(canvas_zoom)
        
    window.setLayout(layout)
            
    return window, AX_large_view, AX_zoom, canvas_large_view, canvas_zoom


def set_recording_params(window, x0=10, y0=30):
    # front text
    Data_label = QtWidgets.QLabel("===> Acquisition parameters:", window)
    Data_label.setMinimumWidth(200)
    Data_label.move(x0, y0)
    # filename text ---> change with open file
    window.filename_textbox = QtWidgets.QLabel('Filename: [...]', window)
    window.filename_textbox.setMinimumWidth(500)
    window.filename_textbox.move(x0+300, y0)
    myFont=QtGui.QFont() # putting a bold font
    myFont.setBold(True)
    window.filename_textbox.setFont(myFont)
    # acquisision time step ---> changed here !
    window.set_acq_dt_text = QtWidgets.QLabel('Acq. Time Step:', window)
    window.set_acq_dt_text.setMinimumWidth(300)
    window.set_acq_dt_text.move(x0, y0+30)
    window.set_acq_dt = QtWidgets.QDoubleSpinBox(window)
    window.set_acq_dt.setMaximumWidth(100)
    window.set_acq_dt.move(x0+100, y0+30)
    window.set_acq_dt.setRange(0.001, 100.0)
    window.set_acq_dt.setDecimals(3)
    window.set_acq_dt.setSuffix("us")
    window.set_acq_dt.setSingleStep(0.001)
    window.set_acq_dt.setValue(DEFAULT_VALUES['dt'])
    # acquisision time step ---> changed here !
    window.set_acq_gain_text = QtWidgets.QLabel('Channel Gain:', window)
    window.set_acq_gain_text.setMinimumWidth(300)
    window.set_acq_gain_text.move(x0+400, y0+30)
    window.set_acq_gain = QtWidgets.QDoubleSpinBox(window)
    window.set_acq_gain.setMaximumWidth(100)
    window.set_acq_gain.setSuffix("uV")
    window.set_acq_gain.setDecimals(3)
    window.set_acq_gain.move(x0+490, y0+30)
    window.set_acq_gain.setRange(0.001, 1000.0)
    window.set_acq_gain.setSingleStep(0.001)
    window.set_acq_gain.setValue(DEFAULT_VALUES['gain'])
    # acquisision channel ---> changed here !
    window.set_acq_channel_text = QtWidgets.QLabel('Channel:', window)
    window.set_acq_channel_text.setMinimumWidth(300)
    window.set_acq_channel_text.move(x0+230, y0+30)
    window.set_acq_channel = QtWidgets.QComboBox(window)
    window.set_acq_channel.currentIndexChanged.connect(window.channel_change)
    window.set_acq_channel.setMaximumWidth(100)
    window.set_acq_channel.addItem("1")
    window.set_acq_channel.move(x0+290, y0+30)

    
def set_analysis_params(window, x0=10, y0=60):
    # front text
    Data_label = QtWidgets.QLabel("===> Analysis parameters:", window)
    Data_label.setMinimumWidth(200)
    Data_label.move(x0, y0)
    # acquisision time step ---> changed here !
    window.set_alpha_text = QtWidgets.QLabel('Alpha:', window)
    window.set_alpha_text.move(x0+0, y0+30)
    window.set_alpha = QtWidgets.QDoubleSpinBox(window)
    window.set_alpha.setMaximumWidth(60)
    window.set_alpha.move(x0+45, y0+30)
    window.set_alpha.setRange(0.01, 10.0)
    window.set_alpha.setDecimals(2)
    window.set_alpha.setSingleStep(0.01)
    window.set_alpha.setValue(DEFAULT_VALUES['alpha'])
    # Tstate window step ---> changed here !
    window.set_Tstate_text = QtWidgets.QLabel('Tstate:', window)
    window.set_Tstate_text.move(x0+115, y0+30)
    window.set_Tstate = QtWidgets.QDoubleSpinBox(window)
    window.set_Tstate.setMaximumWidth(80)
    window.set_Tstate.setSuffix("ms")
    window.set_Tstate.setDecimals(1)
    window.set_Tstate.move(x0+160, y0+30)
    window.set_Tstate.setRange(1, 2000.0)
    window.set_Tstate.setSingleStep(0.1)
    window.set_Tstate.setValue(DEFAULT_VALUES['Tstate'])
    # Tsmoothing ---> changed here !
    window.set_Tsmooth_text = QtWidgets.QLabel('Tsmooth:', window)
    window.set_Tsmooth_text.move(x0+250, y0+30)
    window.set_Tsmooth = QtWidgets.QDoubleSpinBox(window)
    window.set_Tsmooth.setMaximumWidth(70)
    window.set_Tsmooth.setSuffix("ms")
    window.set_Tsmooth.setDecimals(1)
    window.set_Tsmooth.move(x0+310, y0+30)
    window.set_Tsmooth.setRange(1., 200.0)
    window.set_Tsmooth.setSingleStep(0.1)
    window.set_Tsmooth.setValue(DEFAULT_VALUES['Tsmooth'])
    # Root-Freq ---> changed here !
    window.set_rootfreq_text = QtWidgets.QLabel('f0:', window)
    # window.set_rootfreq_text.setMinimumWidth(200)
    window.set_rootfreq_text.move(x0+395, y0+30)
    window.set_rootfreq = QtWidgets.QDoubleSpinBox(window)
    window.set_rootfreq.setMaximumWidth(70)
    window.set_rootfreq.setSuffix("Hz")
    window.set_rootfreq.setDecimals(1)
    window.set_rootfreq.move(x0+415, y0+30)
    window.set_rootfreq.setRange(0.1, 100.0)
    window.set_rootfreq.setSingleStep(0.1)
    window.set_rootfreq.setValue(DEFAULT_VALUES['Root_freq'])
    # Band-Factor ---> changed here !
    window.set_bandfactor_text = QtWidgets.QLabel('w0:', window)
    # window.set_bandfactor_text.setMinimumWidth(200)
    window.set_bandfactor_text.move(x0+495, y0+30)
    window.set_bandfactor = QtWidgets.QDoubleSpinBox(window)
    window.set_bandfactor.setMaximumWidth(70)
    window.set_bandfactor.setDecimals(1)
    window.set_bandfactor.move(x0+525, y0+30)
    window.set_bandfactor.setRange(0.1, 100.0)
    window.set_bandfactor.setSingleStep(0.1)
    window.set_bandfactor.setValue(DEFAULT_VALUES['Band_Factor'])
    # N wavelets ---> changed here !
    window.set_N_wvlts_text = QtWidgets.QLabel('N wavelets:', window)
    # window.set_N_wvlts_text.setMinimumWidth(200)
    window.set_N_wvlts_text.move(x0+600, y0+30) # 
    window.set_N_wvlts = QtWidgets.QDoubleSpinBox(window)
    window.set_N_wvlts.setMaximumWidth(50)
    # window.set_N_wvlts.setSuffix("Hz")
    window.set_N_wvlts.setDecimals(0)
    window.set_N_wvlts.move(x0+670, y0+30)
    window.set_N_wvlts.setRange(1, 100)
    window.set_N_wvlts.setSingleStep(1)
    window.set_N_wvlts.setValue(DEFAULT_VALUES['N_wavelets'])
    # Subsampling ---> changed here !
    window.set_subsampling_text = QtWidgets.QLabel('pLFP-Subsampling:', window)
    window.set_subsampling_text.setMinimumWidth(200)
    window.set_subsampling_text.move(x0+730, y0+30)
    window.set_subsampling = QtWidgets.QDoubleSpinBox(window)
    window.set_subsampling.setMaximumWidth(70)
    window.set_subsampling.setSuffix("ms")
    window.set_subsampling.setDecimals(1)
    window.set_subsampling.move(x0+850, y0+30)
    window.set_subsampling.setRange(0.1, 100.0)
    window.set_subsampling.setSingleStep(0.1)
    window.set_subsampling.setValue(DEFAULT_VALUES['Tsubsampling'])
    # # p0 percentile ---> changed here !
    # window.set_p0_percentile_text = QtWidgets.QLabel('p0 percentile:', window)
    # window.set_p0_percentile_text.setMinimumWidth(300)
    # window.set_p0_percentile_text.move(x0+565, y0+30)
    # window.set_p0_percentile = QtWidgets.QDoubleSpinBox(window)
    # window.set_p0_percentile.setMaximumWidth(100)
    # window.set_p0_percentile.setSuffix("%")
    # window.set_p0_percentile.setDecimals(1)
    # window.set_p0_percentile.move(x0+650, y0+30)
    # window.set_p0_percentile.setRange(0.1, 100.0)
    # window.set_p0_percentile.setSingleStep(0.1)
    # window.set_p0_percentile.setValue(DEFAULT_VALUES['p0_percentile'])

        
if __name__ == '__main__':
    import time
    app = QtWidgets.QApplication(sys.argv)
    main = Window(app)
    # main.show()
    sys.exit(app.exec_())
