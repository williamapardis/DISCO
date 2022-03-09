import serial

DISCO = serial.Serial('COM1',9600)

while(True):
    output = "1,1,1,1,1"
    DISCO.write(output.encode())

