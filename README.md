# DISCO Graphic User Interface 
A python QT visual interface for operation of the DISCO Reactive Oxygen Sensor (ROS). Application controls 3 internal parastaltic pumps (Instech), recovers, displays and stores data from main optical transducer (Hamamatsu PMT) and auxillary sensors (Senserion Flow sensors). communicates over a bluetooth 2.0 connection appearing as a vitual comp port (HC06).
# Application
## Setup and Installation

###### Install Git
1. Download and install git for windows [here](https://gitforwindows.org/)
2. next through everything and install
3. Right click on desktop and select "Git Bash Here"
2. Clone repo with application...
```
git clone https://github.com/williamapardis/DISCO.git
```
###### Install Python
1. Install the 3.10.2 release of python by runing python-3.10.2-amd64.exe in the DISCO/install folder or downloading [here](https://www.python.org/downloads/).
- make sure to check Add Python 3.10 to PATH!!!!!!!!!!!!
###### Bluetooth COM Setup
1. Through windows search navigate to the "Bluetooth and other device settings"
2. Pairing device
- Click "Add Bluetooth or other device" 
- In the add a device window click "Bluetooth"
- After giving time to search "HC-06" should appear, click pair/connect
- Password: 1234
3. Check  virtual COM port
- Naviegate to the 

# Emulator
1. install free-virtual-serial-port-tools.exe
2. create a local bridge and record ports
Samsung Galaxy Book 2, 128GB, 12 Display, Windows 10