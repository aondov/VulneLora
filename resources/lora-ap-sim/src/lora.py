import random
import base64
import json
import math

from enum import Enum
from datetime import datetime
from datetime import timedelta

DUTY_CYCLE = 36000
GW_DUTY_CYCLE = 36000
BATTERY_FULL = 100
MIN_HEART_RATE = 50
MAX_HEART_RATE = 150
LORA_VERSION = "1.0"
SLEEP_TIME = 120
CHANNELS = 8
PRE_SHARED_KEY = '+/////v////7////+////wIAAAA='
MAX_X_POSITION = 10000
MAX_Y_POSITION = 10000
TRANS_ANT_GAIN = 2
REC_ANT_GAIN = 8
X_DIRECTIONS = [-1, 1]
Y_DIRECTIONS = [-1, 1]


class LoRa:

    @staticmethod
    def get_snr():
        """
        Randomly generated SNR values between -20 and +10
        :return
        """
        return round(random.uniform(0, 1) * 30 - 20, 1)

    @staticmethod
    def calculate_rssi(tp, gain_t, gain_r, frequency, distance):
        """
        Calculate RSSI based on rx and tx antennas, frequency and distance
        :param tp transmitting power
        :param gain_t gain of transmitter antenna
        :param gain_r gain of receiver antenna
        :param frequency frequency in MHz
        :param distance distance in km
        :return
        """
        print(f"Frequency: {frequency} MHz, Distance: {distance} km")
        # 32.5 is constant value used when a distance is in km and frequency in MHz
        fsl = 32.5 + 20 * math.log(frequency, 10) + 20 * math.log(distance)
        return round(tp + gain_t - fsl + gain_r, 1)

    """
    @staticmethod
    def get_time(data_length, sf=7, cr=1.0, bw=125):
        bit_rate = sf * ((4 / (4 + cr)) / (pow(2, sf) / bw))
        return math.ceil(data_length * 8 * bit_rate)
    """

    @staticmethod
    def get_data(pos_x, pos_y):
        """
        Generate base64 string from input data
        :param pos_x: float
        :param pos_y: int
        :return
        """
        message = str(pos_x) + "," + str(pos_y)
        message_bytes = message.encode('ascii')
        return base64.b64encode(message_bytes).decode('ascii')

    @staticmethod
    def calculate_time_on_air(data_len, sf, bw, cr, percentage):
        """
        Message time on air calculation based on LoRa@FIIT library
        :param data_len: data length in Bytes
        :param sf: int, spreading factor
        :param bw: int, bandwidth in Hz
        :param cr: string, coding rate
        :param percentage: duty cycle percentage
        :return
        """""
        cr = LoRa.get_coding_rate_value(cr)
        time_per_symbol = pow(2, sf) / (bw / 1000)

        lora_fiit_overhead = 12

        if sf > SpreadingFactors.SF10.value:
            optimization = 1
        else:
            optimization = 0

        message_symbols = 8 + ((8 * (lora_fiit_overhead + data_len) - 4 * sf + 28 + 16) / (4 * (sf - 2 * optimization))) * (cr + 4)

        return round(time_per_symbol * message_symbols)

    @staticmethod
    def get_current_time():
        """
        Returns current minutes and seconds within an hour
        :return datetime
        """
        return datetime.now().replace(microsecond=0)

    @staticmethod
    def get_frame_time(airtime):
        """
        Returns current minutes and seconds within an hour
        :return tuple
        """
        send_time = datetime.now()
        receive_time = send_time + timedelta(milliseconds=airtime)
        return send_time, receive_time

    @staticmethod
    def get_future_time():
        """
        Returns current minutes and seconds within an hour
        :return datetime
        """
        return datetime.now().replace(microsecond=0) + timedelta(hours=1)

    @staticmethod
    def should_refresh_duty_cycle(next_refresh_time):
        """
        Returns whether a duty cycle should be refreshed
        :param next_refresh_time:
        :return boolean
        """
        return datetime.now().replace(microsecond=0) >= next_refresh_time

    @staticmethod
    def get_coding_rate_value(cr):
        """
        Get coding rate as a numeric value
        :param cr: string
        :return float
        """
        if cr == CodingRates.CR45.value:
            return 1.0
        elif cr == CodingRates.CR46.value:
            return 2.0
        elif cr == CodingRates.CR47.value:
            return 3.0
        elif cr == CodingRates.CR48.value:
            return 4.0

    @staticmethod
    def is_collision(f, s):
        """
        Checks if there is a collision between two frames
        :param f: first frame to analyse
        :param s: second frame to analyse
        :return boolean, True if there is a collision, otherwise False
        """
        if (
                (s.start <= f.start <= s.end <= f.end) or
                (f.start <= s.start <= f.end <= s.end) or
                (f.start == s.end and s.start == s.end)
        ):
            f_dict = json.loads(str(f.json_message, 'ascii'))
            s_dict = json.loads(str(s.json_message, 'ascii'))
            # print("================================")
            # print(f.json_message)
            # print("-------------")
            # print(s.json_message)
            # print("================================")
            if f_dict['message_body']['sf'] == s_dict['message_body']['sf']:
                return True
        return False


class Acknowledgement(Enum):
    def __str__(self):
        return str(self.value)

    NO_ACK = "UNSUPPORTED"
    OPTIONAL = "VOLATILE"
    MANDATORY = "MANDATORY"

class MessageType(Enum):
    def __str__(self):
        return str(self.value)

    REGR = "REGR"
    REGA = "REGA"
    SETR = "SETR"
    SETA = "SETA"
    RXL = "RXL"
    TXL = "TXL"
    KEYS = "KEYS"
    KEYR = "KEYR"
    KEYA = "KEYA"


class CodingRates(Enum):
    def __str__(self):
        return str(self.value)

    CR45 = "4/5"
    CR46 = "4/6"
    CR47 = "4/7"
    CR48 = "4/8"


class SpreadingFactors(Enum):
    def __int__(self):
        return int(self.value)

    SF6 = 6
    SF7 = 7
    SF8 = 8
    SF9 = 9
    SF10 = 10
    SF11 = 11
    SF12 = 12


class Frequencies(Enum):
    def __int__(self):
        return int(self.value)

    # normal
    F8661 = 866100000
    F8663 = 866300000
    F8665 = 866500000
    # emergency
    F8669 = 866900000
    # register
    F8667 = 866700000


class Bandwidth(Enum):
    def __int__(self):
        return int(self.value)

    BW125 = 125000
    BW250 = 250000
    BW500 = 500000


class Power(Enum):
    def __int__(self):
        return int(self)

    PW15 = 15
    PW14 = 14
    PW13 = 13
    PW12 = 12


# From lora AP concentrator
SUP_FREQUENCIES = [863000000, 100000, 870000000]

REG_FREQUENCIES = [Frequencies.F8667.value]
EMER_FREQUENCIES = [Frequencies.F8669.value]

NORMAL_FREQUENCIES = [
    Frequencies.F8661.value,
    Frequencies.F8663.value,
    Frequencies.F8665.value
]

NET_CONFIG = {
    'normal': {
        'freqs': NORMAL_FREQUENCIES,
        'band': Bandwidth.BW125.value,
        'cr': CodingRates.CR45.value,
        'sf': SpreadingFactors.SF7.value,
        'power': Power.PW13.value
    },
    'reg': {
        'freqs': REG_FREQUENCIES,
        'band': Bandwidth.BW125.value,
        'cr': CodingRates.CR45.value,
        'sf': SpreadingFactors.SF12.value,
        'power': Power.PW15.value
    },
    'emer': {
        'freqs': EMER_FREQUENCIES,
        'band': Bandwidth.BW125.value,
        'cr': CodingRates.CR45.value,
        'sf': SpreadingFactors.SF12.value,
        'power': Power.PW15.value
    }
}

BANDIT_ARMS = [
    {"sf":7,"pw":10,"rw":1},
    {"sf":7,"pw":14,"rw":1},
    {"sf":8,"pw":10,"rw":1},
    {"sf":8,"pw":14,"rw":1},
    {"sf":9,"pw":10,"rw":1},
    {"sf":9,"pw":14,"rw":1},
    {"sf":10,"pw":10,"rw":1},
    {"sf":10,"pw":14,"rw":1},
    {"sf":11,"pw":10,"rw":1},
    {"sf":11,"pw":14,"rw":1},
    {"sf":12,"pw":10,"rw":1},
    {"sf":12,"pw":14,"rw":1}
]

MAX_POWER = Power.PW14.value

FREQUENCIES = [
    Frequencies.F8667.value,
    Frequencies.F8661.value,
    Frequencies.F8663.value,
    Frequencies.F8669.value
]

SPREADING_FACTORS = [
    SpreadingFactors.SF7.value,
    SpreadingFactors.SF8.value,
    SpreadingFactors.SF9.value,
    SpreadingFactors.SF10.value,
    SpreadingFactors.SF11.value,
    SpreadingFactors.SF12.value
]

CODING_RATES = [
    CodingRates.CR45.value,
    CodingRates.CR46.value,
    CodingRates.CR47.value,
    CodingRates.CR48.value
]

BANDS = [
    Bandwidth.BW125.value,
    Bandwidth.BW250.value,
    Bandwidth.BW500.value
]