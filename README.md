# DISCO Graphic User Interface 
A python QT visual interface for operation of the DISCO Reactive Oxygen Sensor (ROS). Application controls 3 internal parastaltic pumps (Instech), recovers, displays and stores data from main optical transducer (Hamamatsu PMT) and auxillary sensors (Senserion Flow sensors). communicates over a bluetooth 2.0 connection appearing as a vitual comp port (HC06).
## Setup and Installation

###### Install Git
1. Download and install git for windows [here](https://gitforwindows.org/)
2. Clone repo with application...
```
git clone git@github.com:williamapardis/DISCO.git
```
###### Install Python
1. Download the 3.10.2 release of python by runing .exe in the install folder or downloading [here](https://www.python.org/downloads/).
###### Bluetooth COM Setup
1. Through windows search navigate to the "Bluetooth and other device settings"
2. Pairing device
- Click "Add Bluetooth or other device" 
- In the add a device window click "Bluetooth"
- After giving time to search "HC-06" should appear, click pair/connect
- Password: 1234
3. Check  virtual COM port
- Naviegate to the 