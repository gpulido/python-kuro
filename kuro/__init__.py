#!/usr/bin/env python3

import time
import serial
from enum import Enum
import logging
import threading
from threading import Thread

from .protocol import *

_LOGGER = logging.getLogger(__name__)


class Gateway():

    def __init__(self, port, baudrate=9600, refresh_time=5):
        """                
        Arguments:
            port {String} -- Serial port string as it is used in pyserial

        Keyword Arguments:

        """
        self.port = port
        self.baudrate = baudrate
        self.lock = threading.Lock()
        self.status = 'off'
        self.ser = None
        self.refresh_time = refresh_time

    def init_refresh(self):
        self.refresh = True
        self.thread = Thread(target=self.refresh_power_status)
        self.thread.start()
        # self.thread.join()

    def stop_refresh(self):
        self.refresh = False

    def configserial(self):
        """
        Configure and open the serial port
        """
        try:
            if '://' in self.port:
                self.ser = serial.serial_for_url(self.port, do_not_open=True)
                self.ser.baudrate = self.baudrate
                self.ser.parity = serial.PARITY_NONE
                self.ser.stopbits = serial.STOPBITS_ONE
                self.ser.bytesize = serial.EIGHTBITS
                self.ser.timeout = 0
                self.ser.xonxoff = False
                self.ser.rtscts = False
                self.ser.dsrdtr = False
                self.ser.open()
                _LOGGER.info("Opened serial port")
            else:
                self.ser = serial.Serial(self.port,
                                         self.baudrate,
                                         bytesize=serial.EIGHTBITS,
                                         timeout=0,
                                         parity=serial.PARITY_NONE,
                                         stopbits=serial.STOPBITS_ONE,
                                         xonxoff=False,
                                         rtscts=False,
                                         dsrdtr=False)

        except Exception as e:
            _LOGGER.error('error open serial port: ' + str(e))
            # exit()

    def executeCommand(self, commandstr):
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
        _LOGGER.info('Gateway writting: ' + str(commandstr))

        with self.lock:
            try:
                response_str = ""
                if not self.ser or not self.ser.isOpen():
                    self.configserial()
                try:
                    self.ser.flushInput()
                    self.ser.flushOutput()             
                except Exception as e1:
                    self.ser.close()
                    self.configserial()
                
                self.ser.write(commandstr)
                time.sleep(0.3)
                response_str = ""
                while True:
                    response = self.ser.readall()
                    response_str += str(response.decode())
                    if (response.decode() == ''):
                        break

            except Exception as e1:
                _LOGGER.exception("error communicating...: " + str(e1))

        return response_str

    def executeCmd(self, cmd, param=None):
        command = KuroCommand(cmd, param, self, True)
        return command.response_type

    def set_volume(self, volume):
        # volume 0..1
        command = VolCommand(volume)
        command.execute(self)
        self.volume = command.volume

    def turn_on(self):
        command = TurnOnCommand()
        command.execute(self)
        self.set_power_status('on')

    def turn_off(self):
        command = TurnOffCommand()
        command.execute(self)
        self.set_power_status('off')

    def set_input(self, input):
        command = InputCommand(input)
        command.execute(self)

    def set_screen_mode(self, screenMode):
        command = ScreenModeCommand(screenMode)
        command.execute(self)

    def volume_up(self):
        command = VolCommand("UP1")
        command.execute(self)
        self.volume = command.volume

    def volume_down(self):
        command = VolCommand("DW1")
        command.execute(self)
        self.volume = command.volume

    def volume_mute(self, mute):
        if mute:
            command = MutedCommand(MutedState.ON)
        else:
            command = MutedCommand(MutedState.OFF)
        command.execute(self)
        self.is_muted = command.is_muted

    def video_mute(self, mute):
        if mute:
            command = PictureOffCommand(PictureOffStatus.ON)
        else:
            command = PictureOffCommand(PictureOffStatus.OFF)
        command.execute(self)

    def osd_state_on(self):
        command = OsdCommand(OsdState.ON)
        command.execute(self)

    def osd_state_off(self):
        command = OsdCommand(OsdState.OFF)
        command.execute(self)

    def get_volume_info(self):
        OsdCommand(OsdState.OFF).execute(self)
        command = VolCommand()
        command.execute(self)
        command2 = MutedCommand()
        command2.execute(self)
        OsdCommand(OsdState.ON).execute(self)
        return {'volume': command.volume if hasattr(command, "volume") else None,
                'mute': command2.is_muted if hasattr(command2, "is_muted") else None,
                'minVolume': 0,
                'maxVolume': 60}

    def get_power_status(self):
        return self.status

    def set_power_status(self, value):
        if self.status != value:
            self.status = value
            _LOGGER.info("set status to: " + value)

    def refresh_power_status(self):
        while self.refresh:
            response_type = self.executeCmd("VMT")

            if response_type == ResponseType.SUCCESS:
                self.set_power_status('on')
            elif response_type != ResponseType.ERROR or response_type == ResponseType.NOT_PROCESSED:
                self.set_power_status('off')

            time.sleep(self.refresh_time)

    def get_input_list(self):
        return {member.describe(): member for member in InputType}

    def get_screen_mode_list(self):
        return {member.describe(): member for member in ScreenMode}

    def get_status(self):
        #command = KuroCommand("ACL")
        # self.executeCommand(command)

        OsdCommand(OsdState.OFF).execute(self)
        inputCommand = InputCommand()
        inputCommand.execute(self)
        avsCommand = AVSCommand()
        avsCommand.execute(self)
        screenModecommand = ScreenModeCommand()
        screenModecommand.execute(self)
        OsdCommand(OsdState.ON).execute(self)

        return {'input': inputCommand.input_type if hasattr(inputCommand, "input_type") else None,
                'avs':  avsCommand.avsType if hasattr(avsCommand, "avsType") else None,
                'screenMode': screenModecommand.screenMode if hasattr(screenModecommand, "screenMode") else None}


if __name__ == '__main__':
    logFormatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    rootLogger.setLevel(logging.DEBUG)
    gat = Gateway('rfc2217://192.168.1.20:7000')
    gat.init_refresh()
    content_mapping = gat.get_input_list()

    print(gat.get_power_status())
