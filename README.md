# GF2 Software Project: Logic Simulator
## Group 4: jt741, pp490, and tnr22

### Initial Setup:
Clone the repository using the command:
```
git clone https://github.com/Sheev13/logic-simulator.git
```
If you are using the Linux system in the DPO, make sure to start an Anaconda shell and navigate to the correct directory using:
```
cd logic-simulator/final
```
To run the Logic Simulator in **English**, run the command:
```
LANG=en_EN.utf-8 ./logsim.py
```
To run the Logic Simulator in **Spanish**, run the command:
```
LANG=es_ES.utf-8 ./logsim.py
```
The above commands will prompt you to select a file to load. To immediately load a file upon start-up run the command:

```
LANG=en_EN.utf-8 ./logsim.py <file-path>
```
  or 
```
LANG=es_ES.utf-8 ./logsim.py <file-path>
```
depending on your language preference.

### For developers - running Pytests
To run pytests, make sure to first install the requirements by running the command:

```
pip install -r requirements.txt
```

You may then run tests by running the command:

```
pytest
```
