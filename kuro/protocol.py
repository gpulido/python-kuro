
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
        print("kurocommand" + response_str)
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
        print(self.response_type)
        if self.response_type == ResponseType.SUCCESS:
            self.response = self.params
        elif self.response_type == ResponseType.NOT_PROCESSED:
            idx = response_str.find(self.cmd) + len(self.cmd)
            self.response = response_str[idx:idx + 3]
        else:
            self.response = None
        logging.debug("response" + str(self.response))
        print("response" + str(self.response))

class OsdState(Enum):
    NONE = None
    OFF = "00"
    ON = "01"

class OsdCommand(ParameterCommand):

    def __init__(self, osd_state = OsdState.NONE):
        super().__init__("OSD", osd_state.value)

    def process_response(self, response):
        super().process_response(response)
        self.is_osd_on = OsdState(self.response[1:]) == OsdState.ON 


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
        elif "UP" in volume or "DW" in volume:
            n_param = volume
        else:
            n_param = str(volume).zfill(3)
        super().__init__("VOL", n_param)
    
    def process_response(self, response_str):
        super().process_response(response_str)
        if self.response_type == ResponseType.NOT_PROCESSED and self.params == None:
            idx = response_str.find(self.cmd) + len(self.cmd)
            response = response_str[idx:idx + 3]
            self.volume = int(response)
        else:
            self.valume = None   

class MutedState(Enum):
    NONE = None
    OFF = "00"
    ON = "01"

class MutedCommand(ParameterCommand):

    def __init__(self, muted_state = MutedState.NONE):
        super().__init__("AMT", muted_state.value)

    def process_response(self, response):
        super().process_response(response)
        if self.response_type == ResponseType.NOT_PROCESSED and self.params == None:
            self.is_muted = MutedState(self.response[1:])    

class ChannelDirection(Enum):
    FORWARD = "FWD"
    REVERSE = "REV"

class ChangeChannelCommand(ParameterCommand):

    def __init__(self, channel_direction):
        super().__init__("CHN", channel_direction.value) 


class InputType(Enum):
    NONE = None
    INPUT_1 = "01"
    INPUT_2 = "02"
    INPUT_3 = "03"
    INPUT_4 = "04"
    INPUT_5 = "05"
    PC = "06"
    ANALOG = "81"
    TERRESTRIAL = "82"
    DIGITAL = "83"
    HOME_MEDIA_GALLERY = "88"
    
    def describe(self):
        return str(self.name).replace( "_"," ").title()

class TunerType(Enum):
    NONE = None
    ANALOG = "INA"
    TERRESTRIAL = "INC"
    DIGITAL = "IND"
    HOME_MEDIA_GALLERY = "INH"

tuner_sub_input = {
    InputType.ANALOG : TunerType.ANALOG,
    InputType.TERRESTRIAL : TunerType.TERRESTRIAL,
    InputType.DIGITAL : TunerType.DIGITAL,
    InputType.HOME_MEDIA_GALLERY : TunerType.HOME_MEDIA_GALLERY,

}



class InputCommand(ParameterCommand):
#TODO: manage XXX
    def __init__(self, inputType = InputType.NONE, channel = None):
        if inputType in tuner_sub_input.keys():
            if inputType == InputType.TERRESTRIAL:
                super().__init__(tuner_sub_input[inputType], channel)
            else:
                super().__init__(tuner_sub_input[inputType])
        else:
            super().__init__("INP", inputType.value)
    
    def process_response(self, response):
        super().process_response(response)
        if self.response_type == ResponseType.SUCCESS and self.params == None:
            self.input_type = InputType.NONE
        else:
            self.input_type = InputType(self.response[1:])


class MultiScreenStatus(Enum):
    NONE = None
    SINGLE_WINDOW = "00"
    MULTI_WINDOW = "01"
    PIP_LOWER_RIGHT = "02"
    PIP_UPPER_RIGHT = "03"
    PIP_UPPER_LEFT = "04"
    PIP_LOWER_LEFT = "05"
    SWAP = "06"

class MultiScreenCommand(ParameterCommand):

    def __init__(self, screenMode = MultiScreenStatus.NONE):
        super().__init__("MST", MultiScreenStatus.value)

    def process_response(self, response):
        super().process_response(response)
        self.multi_screen_status = MultiScreenStatus(self.response[1:])

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

    def __init__(self, avsType = AVSType.NONE):
        super().__init__("AVS", avsType.value)

    def process_response(self, response):
        super().process_response(response)
        if self.response_type == ResponseType.SUCCESS and self.params == None:
            self.avsType = AVSType.NONE
        else:
            self.avsType = AVSType(self.response[1:])


class ScreenMode(Enum):
    NONE = None
    DOTbyDOT = "00"
    FOUR_THIRD = "01"
    FULL = "02"
    ZOOM = "03"
    #CINEMA = "04"
    WIDE = "05"
    #FULL_14_9 = "07"
    #CINEMA_14_9= "08"
    AUTO = "11"
    WIDE2 = "12"

class ScreenModeCommand(ParameterCommand):

    def __init__(self, screenMode = ScreenMode.NONE):
        super().__init__("SZM", screenMode.value)

    def process_response(self, response):
        super().process_response(response)
        if self.response_type == ResponseType.SUCCESS and self.params == None:
            self.screenMode = ScreenMode.NONE
        else:
            self.screenMode = ScreenMode(self.response[1:])


class RemoteCommandType(Enum):
    R_0 = "00"
    R_1 = "01"
    R_2 = "02"
    R_3 = "03"
    R_4 = "04"
    R_5 = "05"
    R_6 = "06"
    R_7 = "07"
    R_8 = "08"
    R_9 = "09"
    RIGHT = "10"
    LEFT = "11"
    UP = "12"
    DOWN = "13"
    ENTER = "14"
    RED = "15"
    GREEN = "16"
    YELLOW = "17"
    BLUE = "18"
    HOME_MENU = "25"
    DOT = "38"
    CHANNEL_ENTER = "39"
    CHANNEL_RETURN = "40"
    DISPLAY = "41"
    RETURN = "42"
    STOP = "49"
    PLAY = "50"
    PAUSE = "51"
    FF = "52"
    REW = "53"
    HDMI_CTRL = "54"
    TOOLS = "55"
    EXIT = "56"

class RemoteCommand(ParameterCommand):

    def __init__(self, remote_command):
        super().__init__("RMC", remote_command.value)

    def process_response(self, response):
        super().process_response(response[1:])

class PictureOffStatus(Enum):
    NONE = None
    OFF = "00"
    ON = "01"

class PictureOffCommand(ParameterCommand):

    def __init__(self, picture_off_status = PictureOffStatus.NONE):
        super().__init__("VMT", picture_off_status.value)

    def process_response(self, response):
        super().process_response(response)
        if self.response_type == ResponseType.SUCCESS and self.params == None:
            self.input_type = PictureOffStatus.NONE
        else:
            self.is_muted = PictureOffStatus(self.response[1:])
