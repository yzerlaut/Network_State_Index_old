import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np
from scipy import signal
from scipy.ndimage.filters import gaussian_filter1d

##############################################
########### Wavelet Transform ################
##############################################

def my_cwt(data, frequencies, dt, w0=6.):
    """
    wavelet transform with normalization to catch the amplitude of a sinusoid
    """
    output = np.zeros([len(frequencies), len(data)], dtype=np.complex)

    for ind, freq in enumerate(frequencies):
        wavelet_data = np.conj(get_Morlet_of_right_size(freq, dt, w0=w0))
        sliding_mean = signal.convolve(data,
                                       np.ones(len(wavelet_data))/len(wavelet_data),
                                       mode='same')
        # the final convolution
        wavelet_data_norm = norm_constant_th(freq, dt, w0=w0)
        output[ind, :] = signal.convolve(data-sliding_mean+0.*1j,
                                         wavelet_data,
                                         mode='same')/wavelet_data_norm
    return output

### MORLET WAVELET, definition, properties and normalization
def Morlet_Wavelet(t, f, w0=6.):
    x = 2.*np.pi*f*t
    output = np.exp(1j * x)
    output *= np.exp(-0.5 * ((x/w0) ** 2)) # (Normalization comes later)
    return output

def Morlet_Wavelet_Decay(f, w0=6.):
    return 2 ** .5 * (w0/(np.pi*f))

def from_fourier_to_morlet(freq):
    x = np.linspace(0.1/freq, 2.*freq, 1e3)
    return x[np.argmin((x-freq*(1-np.exp(-freq*x)))**2)]
    
def get_Morlet_of_right_size(f, dt, w0=6., with_t=False):
    Tmax = Morlet_Wavelet_Decay(f, w0=w0)
    t = np.arange(-int(Tmax/dt), int(Tmax/dt)+1)*dt
    if with_t:
        return t, Morlet_Wavelet(t, f, w0=w0)
    else:
        return Morlet_Wavelet(t, f, w0=w0)

def norm_constant_th(freq, dt, w0=6.):
    # from theoretical calculus:
    n = (w0/2./np.sqrt(2.*np.pi)/freq)*(1.+np.exp(-w0**2/2))
    return n/dt

##################################################
########### Processing of the LFP ################
##################################################

def gaussian_smoothing(Signal, idt_sbsmpl=10.):
    """Gaussian smoothing of the data"""
    return gaussian_filter1d(Signal, idt_sbsmpl)

def preprocess_LFP(data,
                   freqs = np.linspace(50, 300, 5), 
                   new_dt = 5e-3,
                   smoothing=42e-3,
                   percentile_for_p0=0.01,                   
                   pLFP_unit='$\mu$V'):
    """
    performs continuous wavelet transform and smooth the time-varying high-gamma freq power
    """

    # performing wavelet transform
    data['W'] = my_cwt(data['Extra'].flatten(), freqs, data['dt']) 
    data['pLFP_freqs'] = freqs # keeping track of the frequency used

    # taking the mean power over the frequency content considered
    W2 = np.abs(data['W']).mean(axis=0)
    isubsmpl = int(new_dt/data['dt'])
    
    # then smoothing and subsampling
    data['pLFP'] = gaussian_smoothing(\
                                      np.reshape(W2[:int(len(W2)/isubsmpl)*isubsmpl],
                                                 (int(len(W2)/isubsmpl),isubsmpl)).mean(axis=1),
                                      int(smoothing/new_dt)).flatten()
    data['new_dt'] = new_dt
    data['new_t'] = np.arange(len(data['pLFP']))*data['new_dt']
    # find p0
    data['p0'] = np.percentile(data['pLFP'], percentile_for_p0)

def heaviside(x):
    return (np.sign(x)+1)/2

def Network_State_Index(data,
                        p0=0.,
                        alpha=2.):
    
    NSI=np.zeros(len(data['pLFP']))
    # where rhythmicity is matched
    X = (p0+alpha*data['max_low_freqs_power'])-data['sliding_mean']
    NSI = -2*data['max_low_freqs_power']*heaviside(X)+heaviside(-X)*(data['sliding_mean']-p0)
    return NSI

def Validate_Network_States(data, 
                            Tstate=200e-3,
                            Var_criteria=2):
    
    # validate states:
    iTstate = int(Tstate/data['new_dt'])
    # validate the transitions
    data['NSI_validated'] = np.zeros(len(data['pLFP']), dtype=bool)
    data['NSI_unvalidated'] = np.zeros(len(data['pLFP']), dtype=bool)
    for i in np.arange(len(data['pLFP']))[::iTstate][1:-1]:
        if np.array(np.abs(data['NSI'][i-iTstate:i+iTstate]-data['NSI'][i])<=Var_criteria).all():
            data['NSI_validated'][i]=True
        else:
            data['NSI_unvalidated'][i]=True

    data['t_validated'] = data['new_t'][data['NSI_validated']]
    data['i_validated'] = np.arange(len(data['pLFP']))[data['NSI_validated']]

    
def compute_Network_State_Index(data,
                                key='pLFP',
                                freqs = np.linspace(2,10,20),
                                Tstate=200e-3,
                                # Var_criteria=2,
                                alpha=2.85,
                                T_sliding_mean=0.5,
                                already_low_freqs_and_mean=False):
    
    if not already_low_freqs_and_mean:
        # sliding mean
        data['sliding_mean'] = gaussian_smoothing(data[key], int(T_sliding_mean/data['new_dt']))

        # low frequency power
        data['low_freqs'] = freqs # storing the used-freq
        data['W_low_freqs'] = my_cwt(data[key].flatten(), freqs, data['new_dt']) # wavelet transform
        data['max_low_freqs_power'] = np.max(np.abs(data['W_low_freqs']), axis=0) # max of freq.
    
    data['NSI']= Network_State_Index(data,
                                     p0 = data['p0'],
                                     alpha=alpha)
    
    Validate_Network_States(data,
                            Tstate=Tstate,
                            # Var_criteria=Var_criteria,
                            Var_criteria=data['p0'])
    
    
if __name__=='__main__':
    print(gaussian_smoothing(np.linspace(0,100,50), 1.3)) # translating to integer values... so keep in mind
