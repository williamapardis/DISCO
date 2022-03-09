import time
import serial
import random


DISCO = serial.Serial('COM1',9600)

while(True):

    counts  = random.randint(10,50000)
    flowIn  = round(random.uniform(0.00,15.00),2)
    tempIn  = round(random.uniform(15.00,42.00),2)
    flowOut = round(random.uniform(0.00,15.00),2)
    tempOut = round(random.uniform(22.00,37.00),2)

    output = str(flowIn)+','+str(tempIn)+','+str(flowOut)+','+str(tempOut)+','+str(counts)+'\r\n'

    print(output)
    
    DISCO.write(output.encode())

    time.sleep(0.5)

