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
                time.sleep(0.3)
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
        command = VolCommand("UP1")
        self.executeCommand(command)
    
    def volume_down(self):
        command = VolCommand("DW1")
        self.executeCommand(command)
    
    def volume_mute(self, mute):
        if mute:
            command = MutedCommand(MutedState.ON)
        else:
            command = MutedCommand(MutedState.OFF)
        self.executeCommand(command)
    
    def video_mute(self, mute):
        if mute:
            command = PictureOffCommand(PictureOffStatus.ON)
        else:
            command = PictureOffCommand(PictureOffStatus.OFF)
        self.executeCommand(command)
    
    def osd_state_on(self):
        osdCommand = OsdCommand(OsdState.ON)
        self.executeCommand(osdCommand)
    
    def osd_state_off(self):
        osdCommand = OsdCommand(OsdState.OFF)
        self.executeCommand(osdCommand)

    def get_volume_info(self):
        self.executeCommand(OsdCommand(OsdState.OFF))
        command = VolCommand()
        self.executeCommand(command)
        command2 = MutedCommand()
        self.executeCommand(command2)
        self.executeCommand(OsdCommand(OsdState.ON))
        return {'volume' : command.volume if hasattr(command, "volume") else None, 
                'mute' : command2.is_muted if hasattr(command2,"is_muted") else None, 
                'minVolume' : 0, 
                'maxVolume' : 60}
        
    def get_power_status(self):
        command = PictureOffCommand()
        self.executeCommand(command)
        if command.response_type == ResponseType.SUCCESS:
            return 'off'
        elif command.response_type != ResponseType.ERROR:
            return 'on'
    
    def get_input_list(self):
        return [(member.describe(),member) for member in InputType]

    def get_status(self):
        self.executeCommand(OsdCommand(OsdState.OFF))
        inputCommand = InputCommand()
        self.executeCommand(inputCommand)
        avsCommand = AVSCommand()
        self.executeCommand(avsCommand)
        screenModecommand = ScreenModeCommand()
        self.executeCommand(screenModecommand)
        self.executeCommand(OsdCommand(OsdState.ON))
        
        return {'input' : inputCommand.input_type if hasattr(inputCommand, "input_type") else None,
                'avs' :  avsCommand.avsType if hasattr(avsCommand, "avsType") else None,
                'screenMode' : screenModecommand.screenMode if hasattr(screenModecommand, "screenMode") else None}
                

if __name__ == '__main__':
    #print (singlemask(2).decode('utf-8'))

    #manual = MethodCall("selve.GW.iveo.getIDs",[])
    gat = Gateway('rfc2217://192.168.1.20:7000')
    power_status = gat.get_power_status()
    print(power_status)
    gat.turn_on()
    vol_status = gat.get_volume_info()
    print(vol_status)
    #gat = Gateway('')
    #gat.executeCommand(MutedCommand(MutedState.ON))



