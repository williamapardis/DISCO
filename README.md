# DISCO

![image](https://user-images.githubusercontent.com/57682790/236154424-ac552e55-aca1-463a-8453-431461e9321c.png)

![image](https://user-images.githubusercontent.com/57682790/236510513-a3f3bdfe-5adb-431b-92fb-c2289edfb4a4.png)

## Instrument
<table>
  <tr>
    <td>Drawing</td>
    <td>On Deck</td>
    <td>In Water</td>
  </tr>
  <tr>
    <td><img src="https://user-images.githubusercontent.com/57682790/236510606-38789243-a0e9-4dab-b485-3744a880a0c2.png"></td>
    <td><img src="https://user-images.githubusercontent.com/57682790/236510767-185df3e4-a2bd-4cce-9d7c-d95b94953fef.png"></td>
    <td><img src="https://user-images.githubusercontent.com/57682790/236510871-7a0bc613-8806-48a2-8b87-8f8fd02fb018.png"></td>
  </tr>
</table>


A python QT visual interface for operation of the DISCO Reactive Oxygen Sensor (ROS). Application runs on a oil compensated Samsung Galaxy Book 2, 128GB, 12 Display, Windows 10. Application controls 3 internal parastaltic pumps (Instech), recovers, displays and stores data from main optical transducer (Hamamatsu PMT) and auxillary sensors (Senserion Flow sensors). communicates over a bluetooth 2.0 connection appearing as a vitual comp port (HC06).
# Hardware

# Software
## Application or Graphic User Interface
### Setup and Installation
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
- After giving time to search "HC-05" should appear, click pair/connect
- Password: 1234
3. Check  virtual COM port
- Navigate to the 
### Dependencies

## Emulator
1. install free-virtual-serial-port-tools.exe
2. create a local bridge and record ports

# Utilities

## Troubleshooting
When running the application after installing python several errors can occur...

1)  Error: 

    "ImportError: cannot import name 'Serial' from 'serial'"
    
    Solution: 
    
    1. Uninstall the serial package using the command line by typing "pip uninstall pyserial"
    2. Reinstall pyserial type"pip install pyserial"
    
2) Error:

   Solution:
   
