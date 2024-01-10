import string
import random


class QueuedMessage:
    def __init__(self, json_message, start, end):
        """
        Constructor
        :param json_message: message as json-bytes
        :param start: datetime, message send time
        :param end: datetime, message received time
        """
        self.id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        self.json_message = json_message
        self.start = start
        self.retries = 0
        self.end = end


class QueuedReply:
    def __init__(self, id, message):
        """
        Constructor
        :param id: string, message identifier
        :param message: dict, json mesage
        """
        self.id = id
        self.message = message
