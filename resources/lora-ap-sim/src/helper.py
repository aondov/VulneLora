import json


class Helper:
    @staticmethod
    def to_json(message):
        """
        Returns a json bytes-like message
        :param message: dictionary
        :return bytes
        """
        json_message = json.dumps(message, separators=(',', ':'), sort_keys=True)
        return json_message.encode('ascii')

    @staticmethod
    def from_json(json_message):
        """
        Return a json message as a dictionary
        :param json_message: bytes-like message
        :return dictionary
        """
        print("================================")
        print(json_message)
        print("================================")
        return json.loads(json_message)
