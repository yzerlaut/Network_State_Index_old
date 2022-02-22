import sys, os, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np
import os

def load_formatted_data(filename):
    
    print('Opening: ', filename)

    # -----------------------------
    # NPZ file
    if filename.endswith('.npz'):
        data = dict(np.load(filename))
        data['Channel_Keys'] = []
        for key in data.keys():
            if key not in ['dt', 'params', 't', 'Channel_Keys']:
                data['Channel_Keys'].append(key)
                
    # -----------------------------
    # ABF file (from pClamp recording software, Axon Instruments / Molecular Device)
    elif filename.endswith('.abf'):
        data = load_axon_file(filename)
        print(data)
        
    # -----------------------------
    # HDF5 file (from RTXI, custom softwares, etc..)
    elif filename.endswith('.h5'):
        data = load_dict_from_hdf5(filename)
        data['Channel_Keys'] = []
        for key in data.keys():
            if key not in ['dt', 'params', 't', 'Channel_Keys']:
                data['Channel_Keys'].append(key)
        try:
            data['dt'] = float(data['params']['dt'])
        except KeyError:
            pass
    else:
        data = {}
    return data

"""
HDF5 format
---> also used for the data output !
"""
import h5py

def make_writable_dict(dic):
    dic2 = dic.copy()
    for key, value in dic.items():
        if (type(value)==float) or (type(value)==int):
            dic2[key] = np.ones(1)*value
        if type(value)==list:
            dic2[key] = np.array(value)
    return dic2

def save_dict_to_hdf5(dic, filename):
    """
    ....
    """
    with h5py.File(filename, 'w') as h5file:
        recursively_save_dict_contents_to_group(h5file, '/', dic)

def recursively_save_dict_contents_to_group(h5file, path, dic):
    """
    ....
    """
    for key, item in dic.items():
        if isinstance(item, (np.ndarray, np.int64, np.float64, str, bytes)):
            h5file[path + key] = item
        elif isinstance(item, dict):
            recursively_save_dict_contents_to_group(h5file, path + key + '/', item)
        elif isinstance(item, tuple):
            h5file[path + key] = np.array(item)
        elif isinstance(item, list):
            h5file[path + key] = np.array(item)
        elif isinstance(item, float):
            h5file[path + key] = np.array(item)
        else:
            raise ValueError('Cannot save %s type'%type(item))

def load_dict_from_hdf5(filename):
    """
    ....
    """
    with h5py.File(filename, 'r') as h5file:
        return recursively_load_dict_contents_from_group(h5file, '/')

def recursively_load_dict_contents_from_group(h5file, path):
    """
    ....
    """
    ans = {}
    for key, item in h5file[path].items():
        if isinstance(item, h5py._hl.dataset.Dataset):
            ans[key] = item.value
        elif isinstance(item, h5py._hl.group.Group):
            ans[key] = recursively_load_dict_contents_from_group(h5file, path + key + '/')
    return ans


"""
Axon Instruments format
"""
import pyabf

def load_axon_file(filename, zoom=[0,np.inf]):

    try:
        abf = pyabf.ABF(filename)
        channels = abf.adcNames
        formatted_data = {'Channel_Keys':channels}
        formatted_data['dt'] = 1./abf.dataRate

        for i, channel in enumerate(channels):
            abf.setSweep(sweepNumber=0, channel=i)
            formatted_data[channel] = abf.sweepY

        return formatted_data
    
    except FileNotFoundError:
        print('File not Found !')
        return {}
    
# if __name__ == '__main__':
#     import sys
#     filename = sys.argv[-1]
#     data = load_axon_file(filename)
#     print(data.keys())
#     # AxonIO(filename).read_block(lazy=False)
#     print(get_metadata(filename))
#     t, data = load_file(filename, zoom=[-5.,np.inf])
#     # for i in range(10):
#     #     plt.plot(t, data[0][i])
#     plt.plot(t, data[0])
#     plt.show()
