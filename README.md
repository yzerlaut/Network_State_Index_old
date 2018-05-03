# Identifying Network State from Extracellular Recordings during Wakefulness in Neocortex

Implements a quantitative characterization of network states in neocortex from the signal recorded by an extracellular electrode.

[The source for the impementation is available here][src].

See the paper details about the method.

----

## Dependencies

[Python 3][python], [Numpy][numpy], [Scipy][scipy], [Neo][neo], [PyQT][pyqt]

----

## Installation

- Install a scientific python distribution (the [Anaconda version][anaconda] is a very good one). Choose the Python 3 version. It contains [Numpy][numpy] and [Scipy][scipy].

- Install PyQT5 (for the graphical interface): open the terminal (or the MsWin Command Prompt) and run:
```
pip install PyQT5
```

- Install Neo (to between electrophysiological data): open the terminal (or the MsWin Command Prompt) and run:
```
pip install neo
```

- Download the present code
  1) If you have git
  ```
	git clone https://github.com/yzerlaut/Waking_State_Index.git
  ```

  2) If you don't, download the zip archive: [https://github.com/yzerlaut/Waking_State_Index/archive/master.zip] and extract it.

----

## Run the program
  Open the terminal (or the MsWin Command Prompt)
  
  ```
  cd path_where_you_have_extracted_or_cloned_the_archive/Waking_State_Index/
  
  python src/gui.py
  ```

----

## GUI Demo

![screenshot](doc/screenshot.png)


## Electrophysiological data supported

- Axon Instruments (pClamp) ".abf" format

- Binary format ()

- Numpy storing formats (either ".npy" or ".npz")


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