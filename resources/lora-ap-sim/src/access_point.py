import json
from datetime import timedelta

from lora import NET_CONFIG
from lora import GW_DUTY_CYCLE
from lora import LORA_VERSION
from lora import SUP_FREQUENCIES
from lora import SPREADING_FACTORS
from lora import CODING_RATES
from lora import BANDS
from lora import MAX_POWER
from lora import LoRa
from lora import MessageType


class AccessPoint:
    def __init__(self, hw_id, conn):
        self.hw_id = hw_id
        self.net_config = NET_CONFIG
        self.duty_cycle_refresh = LoRa.get_future_time()
        self.duty_cycle = GW_DUTY_CYCLE
        self.conn = conn
        self.duty_cycle_na = 0
        self.x = 0
        self.y = 0

    def generate_setr(self):
        """
        Generates SETR message as a python dictionary and returns json bytes
        :return bytes
        """
        message = {}
        message_body = {}
        lora_stand = {}

        message['message_name'] = MessageType.SETR.value
        message_body['id'] = self.hw_id
        message_body['ver'] = LORA_VERSION
        message_body['m_chan'] = True
        message_body['channels'] = 8
        message_body['sup_freqs'] = SUP_FREQUENCIES
        message_body['sup_sfs'] = SPREADING_FACTORS
        message_body['sup_crs'] = CODING_RATES
        message_body['sup_bands'] = BANDS
        message_body['max_power'] = MAX_POWER

        lora_stand['name'] = "LoRa@FIIT"
        lora_stand['version'] = "1.0"

        message_body['lora_stand'] = lora_stand
        message['message_body'] = message_body

        json_message = json.dumps(message, separators=(',', ':'), sort_keys=True)
        return json_message.encode('ascii')

    def send_setr(self):
        """
        Sends SETR message, receives reply adn passes to for processing
        :return
        """
        setr_message = self.generate_setr()
        reply = self.conn.send_data(setr_message)
        self.process_reply(reply)

    def process_reply(self, reply):
        """
        If there is a reply, process it
        :param reply:
        :return
        """
        if reply is not None:
            try:
                print("================================")
                print(reply)
                print("================================")
                message = json.loads(str(reply, 'ascii'))
                message_name = message['message_name']

                if message_name == 'SETA':
                    print("Received SETA message")
                    # self.process_seta(message)
                else:
                    print("Unknown message type")
            except ValueError:
                print("Could not deserialize JSON object")
        else:
            print("No reply")

    def set_remaining_duty_cycle(self, time_on_air):
        """
        Checks AP duty cycle and refresh it if duty cycle refresh
        Returns 0 if available and substracts duty cycle
        :param time_on_air: int, time on air of message
        :return int, 0 if available, 1 if not available
        """
        print("Access point duty cycle is {0} ms. Next refresh {1}".format(self.duty_cycle, self.duty_cycle_refresh))

        if LoRa.should_refresh_duty_cycle(self.duty_cycle_refresh):
            self.duty_cycle = GW_DUTY_CYCLE
            self.duty_cycle_na = 0
            print('{0}: Duty cycle refreshed to {1}s'.format(self.hw_id, self.duty_cycle))
            self.duty_cycle_refresh = LoRa.get_future_time()

        if self.duty_cycle - time_on_air > 0:
            self.duty_cycle -= time_on_air
            return 0

        self.duty_cycle_na = 1
        return self.duty_cycle_na

    def set_position(self, x, y):
        """
        Sets the position of an Access Point withing a specified area
        :param x:
        :param y:
        :return:
        """
        self.x = x
        self.y = y
