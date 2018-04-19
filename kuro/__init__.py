#!/usr/bin/env python3

import time
import serial
from enum import Enum
import logging

from kuro.protocol import *

class Gateway():   

    def __init__(self, port, baudrate = 9600):
        """                
        Arguments:
            port {String} -- Serial port string as it is used in pyserial
        
        Keyword Arguments:
            discover {bool} -- True if the gateway should try to discover 
                               the devices on init (default: {True})
        """
        self.port = port
        self.baudrate = baudrate

    
    def configserial(self):
        """
        Configure the serial port
        """
        if '://' in self.port:
            self.ser = serial.serial_for_url(self.port)
        else:
            self.ser = serial.Serial(self.port)
            
        self.ser.baudrate = self.baudrate
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits=serial.STOPBITS_ONE
        self.ser.bytesize=serial.EIGHTBITS
        self.ser.timeout = 0
        self.ser.xonxoff = False
        self.ser.rtscts = False
        self.ser.dsrdtr = False

            
    def executeCommand(self, command):
        """[summary]
        Execute the given command using the serial port.
        It opens a communication to the serial port each time a
        command is executed.
        At this moment it doesn't keep a queue of commands. If
        a command blocks the serial it will wait.
        
        Arguments:
            command {protocol.MethodCall} -- Command to be send 
            through the serial port
        
        Returns:
            MethodResponse -- if the command was executed 
            sucessufully
            ErrorResponse -- if the gateway returns an error
        """
        commandstr = command.serialize()
        logging.info('Gateway writting: ' + str(commandstr))
        print('Gateway writting: ' + str(commandstr))

        try:
            self.configserial()

        except Exception as e:            
            logging.error ('error open serial port: ' + str(e))
            exit()
        
        if self.ser.isOpen():
            try:
                self.ser.flushInput()
                self.ser.flushOutput()
                
                self.ser.write(commandstr)
                time.sleep(0.5)
                response_str = "" 
                while True:
                    response = self.ser.readall()
                    response_str += str(response.decode())
                    #print(response_str)
                    logging.info('read data: ' + response_str)
                    if (response.decode()== ''):
                        break
                    
                self.ser.close()
                print(response_str)
                command.process_response(response_str)
                #return process_response(response_str)
            except Exception as e1:
                logging.exception ("error communicating...: " + str(e1))
        else:
            logging.error ("cannot open serial port")
        
        return None
    
    def executeCmd(self, cmd, param):
        command = KuroCommand(cmd, param)
        self.executeCommand(command)

    def set_volume(self, volume):
        #volume 0..1
        command = VolCommand(volume)
        self.executeCommand(command)

    def turn_on(self):
        command = TurnOnCommand()
        self.executeCommand(command)
    
    def turn_off(self):
        command = TurnOffCommand()
        self.executeCommand(command)

    def volume_up(self):
        command = TurnOffCommand()
        self.executeCommand(command)
    
    def volume_down(self):
        command = TurnOffCommand()
        self.executeCommand(command)


 

if __name__ == '__main__':
    #print (singlemask(2).decode('utf-8'))

    #manual = MethodCall("selve.GW.iveo.getIDs",[])
    gat = Gateway('')
    gat.executeCommand(MutedCommand(MutedState.ON))



