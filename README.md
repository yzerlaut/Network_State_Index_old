# Network State Index

#### Identifying Network State from Extracellular Recordings during Wakefulness in Neocortex

This module provides a quantitative characterization of network states in neocortex from extracellular signals. It implements the analysis described in the following article (please cite if you use this code !):
> Network States Classification based on Local Field Potential Recordings in the Awake Mouse Neocortex
> Yann Zerlaut, Stefano Zucca, Tommaso Fellin, Stefano Panzeri
> bioRxiv 2022.02.08.479568; doi: https://doi.org/10.1101/2022.02.08.479568

----

## GUI Screenshot
![screenshot](doc/screenshot.png)

----

## Installation

1. Install a python distribution for scientific analysis:

   get the [latest Miniconda distribution](https://docs.conda.io/en/latest/miniconda.html) and install it on your home folder.
   
2. Run the following in the [Anaconda prompt](https://docs.anaconda.com/anaconda/user-guide/getting-started/#write-a-python-program-using-anaconda-prompt-or-terminal):

```
git clone https://github.com/yzerlaut/Network_State_Index.gitb
cd Network_State_Index
pip install .
```

If you do not wish to clone the repository you can also directly:
```
pip install git+https://github.com/yzerlaut/Network_State_Index
```


## Usage

- Run the software GUI

```
python -m NSI
```

- Using the notebook implmentation
```
jupyter notebook notebook_demo.ipynb
```

----

## GUI features

### Load data:

##### Electrophysiological data supported

- Axon Instruments (pClamp) ".abf" format

- HDF5 ".h5" format

- Numpy storing formats (".npz" storing a dictionary)

You can set the desired channel to analyze and the gain that should be applied (only if you want it in uV)

### Run analysis:

It computes the NSI measure over the whole data.
It can be a bit long if the data are large.

### Visualize the data and the output of the NSI analysis

In the top 3 plots, we show the full (subsampled) data.

In the bottom 3 plots, we show a zoomed (subsampled) portion of the data. Highlighted with a red filled rectangle in the top plot. 

### Zoom :

- Zoom1: When clicking on this button, you can select a time window in the top plot
- Zoom2: When clicking on this button, you can select a time window in the bottom-Vext plot

### Save the output of the analysis:

The output is stored as an hdf5 datafile.
It containes the sample times of validated network states and their associated NSI level.

[packaging guide]: https://packaging.python.org
[distribution tutorial]: https://packaging.python.org/en/latest/distributing.html
[src]: https://github.com/yzerlaut/waking_state_index
[rst]: http://docutils.sourceforge.net/rst.html
[md]: https://tools.ietf.org/html/rfc7764#section-3.5 "CommonMark variant"
[md use]: https://packaging.python.org/specifications/core-metadata/#description-content-type-optional
[anaconda]: https://www.anaconda.com/download
[numpy]: https://www.numpy.org
[scipy]: https://www.scipy.org
[neo]: http://neuralensemble.org/neo/
[pyqt]: https://www.riverbankcomputing.com/software/pyqt/intro
[python]: https://docs.python.org