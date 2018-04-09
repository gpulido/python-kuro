
from enum import Enum
import logging

STX = chr(0x02)
ETX = chr(0x03)

class ResponseType(Enum):
    ERROR = 0
    SUCCESS = 1
    NOT_PROCESSED = 2

class KuroCommand():

    def __init__(self, cmd, params = None):
        self.cmd = cmd
        self.params = params
    
    def serialize(self):
        if self.params == None:
            return (STX + '**'+ self.cmd + ETX).encode('utf8')
        else:
            return (STX + '**'+ self.cmd + self.params + ETX).encode('utf8')
    
    def process_response(self, response_str):
        if "ERR" in response_str:
            self.response_type = ResponseType.ERROR
        elif "XXX" in response_str:
            self.response_type = ResponseType.SUCCESS
        else:
            self.response_type = ResponseType.NOT_PROCESSED


class ParameterCommand(KuroCommand):
    def __init__(self, cmd, param = None):
        if param == None:
            super().__init__(cmd)
        else:
            super().__init__(cmd, "S" + param)

    def process_response(self, response_str):
        super().process_response(response_str)
        if self.response_type == ResponseType.NOT_PROCESSED:
            self.response = self.params
        elif self.response_type == ResponseType.SUCCESS:
            self.response = response_str[-2:]
        else:
            self.response = None


class EnableOSDCommand(KuroCommand):

    def __init__(self):
        super().__init__("OSD", "01")

class DisableOSDCommand(KuroCommand):

    def __init__(self):
        super().__init__("OSD", "00")

class TurnOnCommand(KuroCommand):

    def __init__(self):
        super().__init__("PON")

class TurnOffCommand(KuroCommand):

    def __init__(self):
        super().__init__("POF")

class VolCommand(KuroCommand):
#max vol 60
    def __init__(self, volume = None):
        if volume == None:
            n_param = None
        # elif "UPn" in param or "Dwn" in param:
        #     n_param = param
        else:
            n_param = str(volume).zfill(3)
        super().__init__("VOL", n_param)
    
    def process_response(self, response_str):
        super().process_response(response_str)
        if self.response_type == ResponseType.SUCCESS:
            self.volume = int(response_str[-3:])
        else:
            self.response = None       

class InputType(Enum):
    NONE = None
    INPUT_1 = "01"
    INPUT_2 = "02"
    INPUT_3 = "03"
    INPUT_4 = "04"
    INPUT_5 = "05"
    PC = "06"

class TunerType(Enum):
    NONE = None
    ANALOG = "81"
    TERRESTRIAL = "82"
    DIGITAL = "83"

class MutedState(Enum):
    NONE = None
    OFF = "00"
    ON = "01"


class MutedCommand(ParameterCommand):

    def __init__(self, muted_state = MutedState.NONE):
        super().__init__("AMT", muted_state.value)

    def process_response(self, response):
        super().process_response(response)
        self.is_muted = MutedState(self.response)

class InputCommand(ParameterCommand):
#TODO: manage XXX
    def __init__(self, inputType = TunerType.NONE):
        super().__init__("INP", inputType.value)
    
    def process_response(self, response):
        super().process_response(response)
        if self.response == "81" or self.response == "82" or self.response == "83":
            self.input_type = InputType.NONE
            self.tuner_type = TunerType(self.response)
        else:
            self.input_type = InputType(self.response)
            self.tuner_type = TunerType.NONE

#este es el cambio de canal. revisar
class ChangeTunerCommand(KuroCommand):
    def __init__(self, tunerType = TunerType.NONE):
        if tunerType != TunerType.NONE:
            n_params = tunerType.value.zfill(3)
        else:
            n_params = None
        super().__init__("INC", n_params)
    
    def process_response(self, response):
        super().process_response(response)
        self.tuner_type = TunerType(response)

#CHN RMC
class AVSType(Enum):
    NONE = None
    STANDARD = "01"
    DYNAMIC = "02"
    MOVIE = "03"
    GAME = "04"
    SPORT = "05"
    PURE = "06"
    USER = "07"
    ISF_DAY = "08"
    ISF_NIGHT = "09"
    OPTIMUN = "10"
    ISF_AUTO = "11"

class AVSCommand(ParameterCommand):

    def __init__(self, screenMode = AVSType.NONE):
        super().__init__("AVS", AVSType.value)

    def process_response(self, response):
        super().process_response(response)
        self.avsType = AVSType(self.response)


class ScreenMode(Enum):
    NONE = None
    DOTbyDOT = "01"
    FOUR_THIRD = "02"
    FULL = "03"
    ZOOM = "04"
    CINEMA = "05"
    WIDE = "06"
    FULL_14_9 = "07"
    CINEMA_14_9= "08"
    AUTO = "09"
    WIDE2 = "10"

class ScreenModeCommand(ParameterCommand):

    def __init__(self, screenMode = ScreenMode.NONE):
        super().__init__("SZM", screenMode.value)

    def process_response(self, response):
        super().process_response(response)
        self.screenMode = ScreenMode(self.response)
        