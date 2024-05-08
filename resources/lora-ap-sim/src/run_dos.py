#!/usr/bin/python

import sys
import random
import time

from ap_dos import AccessPoint
from cc_dos import ConnectionController

conn = None


def main(argv):
    delay = int(argv[0])
    limit = int(argv[1])
    # ap_id_conf_point
    ap_id = str(random.randint(1000, 9999))
    print(f"[INFO]: Created AP with ID {ap_id}")

    # server_conf_point
    conn.connect("127.0.0.1", 8002)
    access_point = AccessPoint(ap_id, conn, delay, limit)
    access_point.send_setr_dos()


if __name__ == "__main__":
    try:
        conn = ConnectionController()
        main(sys.argv[1:])
    except KeyboardInterrupt as e:
        if conn is not None:
            conn.close()
            print("Connection closed")

        print("Python script finished")
